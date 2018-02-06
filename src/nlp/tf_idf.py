import json, tqdm
from src.utils import *
from src.results import *
from src.nlp import Corpus
from gensim.models import TfidfModel


class Tfidf(Corpus):
    """
    Data structure for identifying documents and their corresponding TF-IDF
    scores, with respect to particular keywords and a list of year periods.
    """

    def __init__(
            self, name: str, in_dir: str, text_type: str, year_list: list,
            keys: [list, None] = None, stop_words: [list, set, None]=None):
        """ Initialize TFIDF object. """

        super(Tfidf, self).__init__(name, in_dir, text_type, year_list, keys, stop_words)

        self.tf_idf_models = None

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

    def top_n(self, keyword, n):
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
            for jsondoc in tqdm.tqdm(files):
                if jsondoc[0] != ".":

                    with open(self.in_dir + "/" + jsondoc, 'r', encoding='utf8') as in_file:

                        jsondata = json.load(in_file)
                        year = int(jsondata["Year Published"])

                        if self.year_list[0] <= year < self.year_list[-1]:
                            text = jsondata[self.text_type]

                            # skip this document if it doesn't contain the keyword
                            if keyword in set(text):

                                target = determine_year(year, self.year_list)
                                d2b = self.word_to_id[target].doc2bow(text)
                                tfidf_doc = self.tf_idf_models[target][d2b]

                                for t in tfidf_doc:
                                    if self.word_to_id[target].get(t[0]) == keyword:
                                        results[target].append((jsondoc, t[1]))

        top_results = self._top_n(results, n)

        return TfidfResults(top_results, keyword)


if __name__ == '__main__':

    c = Tfidf(
        'test',
        '/Users/ben/Desktop/work/nlp/british/',
        'Filtered Text',
        [1700, 1720, 1740],
    )

    res = c.top_n('rat', 5)
    res.debug_str()

    print('Done')
