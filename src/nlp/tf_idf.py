import json, tqdm, nltk
from src.utils import *
from src.nlp import Corpus


class TFIDF(Corpus):

    def __init__(self, name: str, in_dir: str, text_type: str, year_list: list, keys: [list, None]=None):
        """ Initialize TFIDF object. """

        super(TFIDF, self).__init__(name, in_dir, text_type, year_list, keys)

