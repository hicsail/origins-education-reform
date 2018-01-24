import nlp.frequency as frequency


class Corpus:
    """
    Data structure for invoking a corpus. A corpus is defined
    as a directory of files (json by default), each storing a volume.
    """

    def __init__(self, i='/tmp', text_type='Words'):
        """ Initialize Corpus object. """

        self.input_dir = i
        self.text_type = text_type

    def word_frequency(self, key_list, year_list):
        return frequency.word_frequency(self.input_dir, self.text_type, key_list, year_list)


