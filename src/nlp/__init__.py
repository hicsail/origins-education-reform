

class Corpus:
    """
    Base class for NLP sub-classes. Defines name of corpus, input path to directory
    of volumes, name of text field to be analyzed, list of years to group the corpus
    over, and (optionally) a list of key words to be analyzed.
    """

    def __init__(self, name: str, in_dir: str, text_type: str, year_list: list,
                 keys: [list, None]=None, stop_words: [list, None] = []):
        """ Initialize Frequency object. """

        self.name = name
        self.in_dir = in_dir
        self.text_type = text_type
        self.year_list = year_list
        self.stop_words = stop_words
        if keys is not None:
            self.key_list = self.build_keys(keys)
        else:
            self.key_list = None

    @staticmethod
    def build_keys(keys: list):
        """ Build list of keyword tuples. """

        return [tuple(k.split()) for k in keys]

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