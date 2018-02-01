import json, tqdm
from src.utils import *
from src.nlp import Corpus
from gensim.models import TfidfModel


class TFIDF(Corpus):
    """
    Data structure for identifying documents and their corresponding
    TF-IDF scores, with respect to particular keywords.
    """

    def __init__(
            self, name: str, in_dir: str, text_type: str, year_list: list,
            keys: [list, None] = None, stop_words: [list, None] = []):
        """ Initialize TFIDF object. """

        super(TFIDF, self).__init__(name, in_dir, text_type, year_list, keys, stop_words)

        self.word_to_id = None
        self.corpora = None
        self.tf_idf_models = None

    def build_dictionaries_and_corpora(self):
        """
        Construct word_to_id that store the word -> id mappings and
        the bag of words representations of the documents in the corpus.
        """

        if self.word_to_id is not None:
            return

        word_to_id_results = gensim_dict(self.year_list)
        corpora_results = list_dict(self.year_list)

        print("Building word_to_id for TF-IDF scoring")

        for subdir, dirs, files in os.walk(self.in_dir):
            for jsondoc in tqdm.tqdm(files):
                if jsondoc[0] != ".":

                    with open(self.in_dir + "/" + jsondoc, 'r', encoding='utf8') as in_file:

                        jsondata = json.load(in_file)
                        year = int(jsondata["Year Published"])

                        # TODO: could extend this to n-grams, but would be slow
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

    def build_tf_idf_models(self):
        """
        Combines the word_to_id and corpora dictionaries
        to construct TF-IDF models for each year period.
        """

        if self.word_to_id is None or self.corpora is None:
            self.build_dictionaries_and_corpora()

        results = gensim_dict(self.year_list)

        for year in self.year_list:
            results[year] = TfidfModel(self.corpora[year], dictionary=self.word_to_id[year])

        self.tf_idf_models = results

    def top_n(self, keyword, n):
        """
        Iterates over the corpus and computes TF-IDF scores for each document,
        with respect to the precomputed TF-IDF models. Extracts results for a
        particular keyword and displays the < n > documents whose TF-IDF scores
        for that keyword are the highest.
        """

        if self.tf_idf_models is None:
            self.build_tf_idf_models()

        print("Calculating {0} files with top TF-IDF scores for {1}".format(n, keyword))

        for subdir, dirs, files in os.walk(self.in_dir):
            for jsondoc in tqdm.tqdm(files):
                if jsondoc[0] != ".":

                    with open(self.in_dir + "/" + jsondoc, 'r', encoding='utf8') as in_file:

                        jsondata = json.load(in_file)
                        year = int(jsondata["Year Published"])

                        # TODO: could extend this to n-grams, but would be slow
                        if self.year_list[0] <= year < self.year_list[-1]:
                            text = jsondata[self.text_type]

                            # skip this document if it doesn't contain the keyword
                            if keyword in set(text):

                                for i in range(len(text) - 1, -1, -1):

                                    # Delete empty strings and single characters
                                    if text[i] in self.stop_words or len(text[i]) < 2:
                                        del text[i]

                                target = determine_year(year, self.year_list)

                                key_id = self.word_to_id[target].token2id[keyword]
                                print(key_id)
                                d2b = self.word_to_id[target].doc2bow(text)

                                tfidf_doc = self.tf_idf_models[target][d2b]

                                for t in tfidf_doc:
                                    if self.word_to_id[target].get(t[0]) == keyword:
                                        print(keyword)


if __name__ == '__main__':

    c = TFIDF(
        'test',
        '/Users/ben/Desktop/work/nlp/british/',
        'Filtered Text',
        [1700, 1720, 1740],
    )

    c.top_n('rat', 5)

    print('Done')
