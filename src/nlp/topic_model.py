import json, tqdm
from src.utils import *
from src.results import *
from src.nlp import Corpus
from gensim.models.ldamodel import LdaModel
from gensim.models.lsimodel import LsiModel
from numpy.random import RandomState
from gensim.models import TfidfModel


class TopicModel(Corpus):
    """
    Data structure for building topic models over a
    corpus, with respect to a list of year periods.
    """

    def __init__(
            self, name: str, in_dir: str, text_type: str, year_list: list,
            keys: [list, None] = None, stop_words: [list, None] = None):
        """ Initialize TopicModel object. """

        super(TopicModel, self).__init__(name, in_dir, text_type, year_list, keys, stop_words)

        self.tf_idf_models = None

    def lda_model(self, num_topics: [int, None] = 10, passes: [int, None] = 1, seed: [int, None] = None):
        """
        Construct LDA topic models for each year in a
        corpus, given a set of parameters.
        """

        if self.word_to_id is None or self.corpora is None:
            self.build_dictionaries_and_corpora()

        results = num_dict(self.year_list)

        if seed is None:

            for year in self.year_list:
                results[year] = \
                    LdaModel(corpus=self.corpora[year], id2word=self.word_to_id[year],
                             num_topics=num_topics, passes=passes)

        else:

            rand = RandomState(seed)
            for year in self.year_list:
                results[year] = \
                    LdaModel(corpus=self.corpora[year], id2word=self.word_to_id[year],
                             num_topics=num_topics, passes=passes, random_state=rand)

        # TODO: wrap in class
        return results

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

    def lsi_model(self, num_topics: [int, None], stochastic: [bool, None] = False):
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

            for year in self.year_list:
                results[year] = \
                    LsiModel(corpus=self.tf_idf_models[year], id2word=self.word_to_id[year],
                             num_topics=num_topics)

        else:

            for year in self.year_list:
                results[year] = \
                    LsiModel(corpus=self.tf_idf_models[year], id2word=self.word_to_id[year],
                             num_topics=num_topics, onepass=False)

        # TODO: wrap in class
        return results
