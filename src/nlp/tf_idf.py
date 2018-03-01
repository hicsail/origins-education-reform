import json, tqdm
from src.utils import *
from src.results import *
from gensim.models import TfidfModel


class Tfidf:
    """
    Data structure for identifying documents and their corresponding TF-IDF
    scores, with respect to particular keywords and a list of year periods.
    """

    def __init__(
            self, name: str, in_dir: str, text_type: str, year_list: list,
            stop_words: [list, set, None]=None):
        """ Initialize TFIDF object. """

        self.name = name
        self.in_dir = in_dir
        self.text_type = text_type
        self.year_list = year_list
        if stop_words is not None:
            self.stop_words = stop_words
        else:
            self.stop_words = {}

        self.tf_idf_models = None
        self.word_to_id = None
        self.corpora = None

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
            for json_doc in tqdm.tqdm(files):
                if json_doc[0] != ".":

                    with open(self.in_dir + "/" + json_doc, 'r', encoding='utf8') as in_file:

                        json_data = json.load(in_file)
                        year = int(json_data["Year Published"])

                        if self.year_list[0] <= year < self.year_list[-1]:
                            text = json_data[self.text_type]

                            for i in range(len(text) - 1, -1, -1):

                                # Delete empty strings and single characters
                                if text[i] in self.stop_words:
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

        results = num_dict(self.year_list)

        for year in self.year_list:
            results[year] = TfidfModel(self.corpora[year], dictionary=self.word_to_id[year])

        self.tf_idf_models = results

    def _top_n(self, results, n):

        top_results = list_dict(self.year_list)

        for year in self.year_list:
            top = sorted(results[year], key=lambda x: x[1])
            top_results[year] = top[:n]

        return top_results

    def top_n(self, keyword: str, n: int):
        """
        Iterates over the corpus and computes TF-IDF scores for each document,
        with respect to the precomputed TF-IDF models. Extracts results for a
        particular keyword and displays the < n > documents whose TF-IDF scores
        for that keyword are the highest.
        """

        if self.tf_idf_models is None:
            self.build_tf_idf_models()

        results = list_dict(self.year_list)

        print("Calculating {0} files with top TF-IDF scores for \'{1}\'".format(n, keyword))

        for subdir, dirs, files in os.walk(self.in_dir):
            for json_doc in tqdm.tqdm(files):
                if json_doc[0] != ".":

                    with open(self.in_dir + "/" + json_doc, 'r', encoding='utf8') as in_file:

                        json_data = json.load(in_file)
                        year = int(json_data["Year Published"])

                        if self.year_list[0] <= year < self.year_list[-1]:
                            text = json_data[self.text_type]

                            # skip this document if it doesn't contain the keyword
                            if keyword in set(text):

                                target = determine_year(year, self.year_list)
                                d2b = self.word_to_id[target].doc2bow(text)
                                tfidf_doc = self.tf_idf_models[target][d2b]

                                for t in tfidf_doc:
                                    if self.word_to_id[target].get(t[0]) == keyword:
                                        results[target].append((json_doc, t[1]))

        top_results = self._top_n(results, n)

        return TfidfResults(top_results, keyword)


