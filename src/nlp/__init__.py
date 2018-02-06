from src.utils import *
import tqdm, json


class Corpus:
    """
    Base class for NLP sub-classes. Defines name of corpus, input path to directory
    of volumes, name of text field to be analyzed, list of years to group the corpus
    over, and (optionally) a list of key words to be analyzed.
    """

    def __init__(self, name: str, in_dir: str, text_type: str, year_list: list,
                 keys: [list, None]=None, stop_words: [list, None] = None):
        """ Initialize Frequency object. """

        self.name = name
        self.in_dir = in_dir
        self.text_type = text_type
        self.year_list = year_list
        if stop_words is None:
            self.stop_words = {}
        else:
            self.stop_words = set(stop_words)
        if keys is not None:
            self.key_list = self.build_keys(keys)
        else:
            self.key_list = None

        self.word_to_id = None
        self.corpora = None

    @staticmethod
    def build_keys(keys: list):
        """ Build list of keyword tuples. """

        return [tuple(k.split()) for k in keys]

    def stop_words_from_json(self, file_path: str, field_name: [str, None]='Words'):
        """ Set stop_words from Json file. """

        with open(file_path, 'r', encoding='utf8') as in_file:

            jsondata = json.load(in_file)
            self.stop_words = set(jsondata[field_name])

    def debug_str(self):
        """ Debug / identify individual Frequency objects. """

        if self.key_list is not None:

            return self.name \
                   + ":" \
                   + ", ".join("\'" + " ".join(k for k in keys) + "\'" for keys in self.key_list)
        else:

            return self.name + ': < No keywords specified >'

    def detect_n(self):
        """ Detect value of n for n-grams. """

        if self.key_list is None:
            return 1

        lengths = set()
        for k in self.key_list:
            lengths.add(len(k))

        assert(len(lengths) == 1)

        return lengths.pop()

    def build_dictionaries_and_corpora(self):
        """
        Construct word_to_id that store the word -> id mappings and the bag of words
        representations of the documents in the corpus. Used for building TF-IDF models
        and LDA / LSI topic models.
        """

        if self.word_to_id is not None:
            return

        word_to_id_results = gensim_dict(self.year_list)
        corpora_results = list_dict(self.year_list)

        print("Building word to ID mappings.")

        for subdir, dirs, files in os.walk(self.in_dir):
            for jsondoc in tqdm.tqdm(files):
                if jsondoc[0] != ".":

                    with open(self.in_dir + "/" + jsondoc, 'r', encoding='utf8') as in_file:

                        jsondata = json.load(in_file)
                        year = int(jsondata["Year Published"])

                        if self.year_list[0] <= year < self.year_list[-1]:
                            text = jsondata[self.text_type]

                            for i in range(len(text) - 1, -1, -1):

                                # Delete empty strings and single characters
                                if text[i] in self.stop_words or len(text[i]) < 2:
                                    del text[i]

                            target = determine_year(year, self.year_list)

                            if len(text) > 0:
                                word_to_id_results[target].add_documents([text])
                                d2b = word_to_id_results[target].doc2bow(text)
                                corpora_results[target].append(d2b)

        self.word_to_id = word_to_id_results
        self.corpora = corpora_results
