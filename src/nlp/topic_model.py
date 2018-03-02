import json
import tqdm
from src.utils import *
from src.results import *
from gensim.models.ldamodel import LdaModel
from gensim.models.lsimodel import LsiModel
from numpy.random import RandomState
from gensim.models import TfidfModel


class TopicModel:
    """
    Data structure for building topic models over a
    corpus, with respect to a list of year periods.
    """

    def __init__(
            self, name: str, in_dir: str, text_type: str,
            year_list: list, stop_words: [list, set, None] = None):
        """ Initialize TopicModel object. """

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
        self.num_docs = None

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
        numdocs = num_dict(self.year_list, nested=0)

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
                            numdocs[target] += 1

                            if len(text) > 0:
                                word_to_id_results[target].add_documents([text])
                                d2b = word_to_id_results[target].doc2bow(text)
                                corpora_results[target].append(d2b)

        self.word_to_id = word_to_id_results
        self.corpora = corpora_results
        self.num_docs = numdocs

        return self

    def lda_model(self, num_topics: [int, None] = 10, passes: [int, None] = 1, seed: [int, None] = None):
        """
        Construct LDA topic models for each year in a
        corpus, given a set of parameters.
        """

        if self.word_to_id is None or self.corpora is None:
            self.build_dictionaries_and_corpora()

        results = num_dict(self.year_list)

        if seed is None:

            for year in self.year_list[:-1]:
                results[year] = \
                    LdaModel(corpus=self.corpora[year], id2word=self.word_to_id[year],
                             num_topics=num_topics, passes=passes)

        else:

            rand = RandomState(seed)
            for year in self.year_list[:-1]:
                results[year] = \
                    LdaModel(corpus=self.corpora[year], id2word=self.word_to_id[year],
                             num_topics=num_topics, passes=passes, random_state=rand)

        return TopicResults(results, self.num_docs)

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

        return self

    def lsi_model(self, num_topics: int=10, stochastic: bool = False):
        """
        Construct LSI topic models for each year in a
        corpus, given a set of parameters.
        """

        if self.word_to_id is None or self.corpora is None:
            self.build_dictionaries_and_corpora()

        if self.tf_idf_models is None:
            self.build_tf_idf_models()

        results = num_dict(self.year_list)

        if not stochastic:

            for year in self.year_list[:-1]:
                results[year] = \
                    LsiModel(corpus=self.tf_idf_models[year][self.corpora[year]],
                             id2word=self.word_to_id[year],
                             num_topics=num_topics
                             )

        else:

            for year in self.year_list[:-1]:
                results[year] = \
                    LsiModel(corpus=self.tf_idf_models[year][self.corpora[year]],
                             id2word=self.word_to_id[year],
                             num_topics=num_topics,
                             onepass=False
                             )

        return TopicResults(results, self.num_docs)

