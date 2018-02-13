import tqdm, json, os, shutil, sys
import nltk
from src.nlp import frequency, tf_idf, topic_model


class Corpus:
    """
    Base class for NLP sub-classes. Defines name of corpus, input path to directory
    of volumes, name of text field to be analyzed, list of years to group the corpus
    over, and (optionally) a list of key words to be analyzed.
    """

    def __init__(self, name: str, in_dir: str):
        """ Initialize Corpus object. """

        self.name = name
        self.in_dir = in_dir

    def debug_str(self):
        """ Debug / identify individual Corpora. """

        return '{0} at {1}'.format(self.name, self.in_dir)

    def frequency(self, name, year_list, key_list, text_type, stop_words: [list, set, None]=None):

        return frequency.Frequency(
            name,
            self.in_dir,
            text_type,
            year_list,
            key_list,
            stop_words
        )

    def tf_idf(self, name, year_list, key_list, text_type, stop_words: [list, set, None]=None):

        return tf_idf.Tfidf(
            name,
            self.in_dir,
            text_type,
            year_list,
            key_list,
            stop_words
        )

    def topic_model(self, name, year_list, text_type, stop_words: [list, set, None]=None):

        return topic_model.TopicModel(
            name,
            self.in_dir,
            text_type,
            year_list,
            stop_words
        )

    @staticmethod
    def build_keys(keys: list):
        """ Build list of keyword tuples. """

        return [tuple(k.split()) for k in keys]

    @staticmethod
    def detect_n(keys):
        """ Detect value of n for n-grams. """

        lengths = set()
        for k in keys:
            lengths.add(len(k))

        assert(len(lengths) == 1)

        return lengths.pop()

    @staticmethod
    def _build_json(title, author, keyword, year, text):
        """ Build json object before writing to disk. """

        jfile = json.dumps({'Title': title,
                            'Author': author,
                            'Keyword': keyword,
                            'Year Published': year,
                            'Text': text
                            },
                           sort_keys=True, indent=4, separators=(',', ': '), ensure_ascii=False)
        return jfile

    def _write_extract(self, out_dir, words, year, index, sub_index, title, author, text):
        """ Write file from sub-corpus to disk. """

        text = [' '.join(w).strip() for w in text]
        words = [' '.join(w).strip() for w in words]
        with open(
                "{0}/{1}_{2}-{3}.json"
                .format(out_dir, str(year), str(index), str(sub_index)),
                'w', encoding='utf-8'
        ) as out:
            out.write(
                self._build_json(
                    title, author, "_".join(words), year, text
                )
            )

    def build_sub_corpus(self, name, output_dir: str, key_list: list, text_type,
                         doc_size: int=20, y_range: [list, None]=None):
        """
        From a larger corpus, construct a sub-corpus containing
        only instances from a list of keywords, with a user-specified
        amount of words around the occurrence.
        """

        # create / overwrite directory where results will be stored
        if not os.path.exists(output_dir):
            os.mkdir(output_dir)
        else:
            shutil.rmtree(output_dir)
            os.mkdir(output_dir)

        if y_range is None:
            y_min = -1*sys.maxsize
            y_max = sys.maxsize
        else:
            y_min = y_range[0]
            y_max = y_range[1]

        index = 0
        subindex = 0

        key_list = self.build_keys(key_list)

        for subdir, dirs, files in os.walk(self.in_dir):
            print("Building sub-corpora.\n")
            for jsondoc in tqdm.tqdm(files):
                if jsondoc[0] != ".":
                    with open(self.in_dir + "/" + jsondoc, 'r', encoding='utf8') as in_file:
                        index += 1
                        jsondata = json.load(in_file)
                        year = int(jsondata["Year Published"])
                        if y_min <= year <= y_max:
                            title = jsondata["Title"]
                            author = jsondata["Author"]
                            text = list(nltk.ngrams(jsondata[text_type], self.detect_n(key_list)))
                            for i in range(len(text)):
                                if text[i] in set(key_list):
                                    subindex += 1
                                    out_text = text[(i - int(doc_size/2)):(i + int(doc_size/2))]
                                    self._write_extract(
                                        output_dir, key_list, year, index,
                                        subindex, title, author, out_text
                                    )

        print("\nDone!\n")

        return Corpus(name, output_dir)