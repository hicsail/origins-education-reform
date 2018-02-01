import json, tqdm, nltk
from src.utils import *
from src.nlp import Corpus
from gensim.models import TfidfModel


class TFIDF(Corpus):

    def __init__(
            self, name: str, in_dir: str, text_type: str, year_list: list,
            keys: [list, None] = None, stop_words: [list, None] = []):
        """ Initialize TFIDF object. """

        super(TFIDF, self).__init__(name, in_dir, text_type, year_list, keys, stop_words)

        self.dictionaries = None
        self.corpora = None
        self.tf_idf_models = None

    def build_dictionaries(self):

        if self.dictionaries is not None:
            return

        dictionary_results = gensim_dict(self.year_list)
        corpora_results = list_dict(self.year_list)

        print("Building dictionaries for TF-IDF scoring")

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
                                dictionary_results[target].add_documents([text])
                                d2b = dictionary_results[target].doc2bow(text)
                                corpora_results[target].append(d2b)

        self.dictionaries = dictionary_results
        self.corpora = corpora_results

    def build_tf_idf_models(self):

        if self.dictionaries is None or self.corpora is None:
            self.build_dictionaries()

        results = gensim_dict(self.year_list)

        for year in self.year_list:
            results[year] = TfidfModel(self.corpora[year], dictionary=self.dictionaries[year])

        self.tf_idf_models = results

    def top_n(self, keyword, n):

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

                                key_id = self.dictionaries[target].token2id[keyword]
                                print(key_id)
                                d2b = self.dictionaries[target].doc2bow(text)

                                tfidf_doc = self.tf_idf_models[target][d2b]

                                for t in tfidf_doc:
                                    if self.dictionaries[target].get(t[0]) == keyword:
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
