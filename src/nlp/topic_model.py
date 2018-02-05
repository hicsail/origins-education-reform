import json, tqdm
from src.utils import *
from src.results import *
from src.nlp import Corpus


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

