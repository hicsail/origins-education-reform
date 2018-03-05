import json, tqdm, nltk
from src.results import *


class RawFrequency:
    """
    Iterates over a corpus and tracks either binary occurrence of a set of keywords
    or their frequency. Binary occurrence is particularly useful for small volumes
    (i.e. - snippet files outputted by build_sub_corpus() in corpus.py.
    """

    def __init__(self, name: str, in_dir: str, text_type: str,
                 keys: [list], binary: bool=False):

        self.name = name
        self.in_dir = in_dir
        self.text_type = text_type
        self.keys = build_keys(keys)
        self.binary = binary

        self.freq_dict = {}

    def detect_n(self):
        """
        Detect value of n for n-grams.
        """

        if self.keys is None:
            return 1

        lengths = set()
        for k in self.keys:
            lengths.add(len(k))

        assert(len(lengths) == 1)

        return lengths.pop()

    def _take_frequencies(self, jsondoc):
        """
        Helper method, measures frequencies in a single volume.
        """

        n = self.detect_n()

        with open(self.in_dir + '/' + jsondoc, 'r', encoding='utf8') as in_file:
            jsondata = json.load(in_file)

            self.freq_dict[jsondoc] = {}
            self.freq_dict[jsondoc]['Year Published'] = int(jsondata['Year Published'])
            self.freq_dict[jsondoc]['Frequencies'] = {}

            if self.binary:
                text = set(nltk.ngrams(jsondata[self.text_type], n))

                for keyword in self.keys:
                    if keyword in text:
                        self.freq_dict[jsondoc]['Frequencies'][' '.join(keyword)] = 1
                    else:
                        self.freq_dict[jsondoc]['Frequencies'][' '.join(keyword)] = 0

            else:
                text = list(nltk.ngrams(jsondata[self.text_type], n))
                self.freq_dict[jsondoc]['Text Length'] = len(text)

                fdist = nltk.FreqDist(text)

                for keyword in self.keys:
                    self.freq_dict[jsondoc]['Frequencies'][' '.join(keyword)] = fdist[keyword]

    def take_frequencies(self):
        """
        Build raw frequency tables.
        """

        for subdir, dirs, files in os.walk(self.in_dir):
            for jsondoc in tqdm.tqdm(files):
                if jsondoc[0] != '.':
                    self._take_frequencies(jsondoc)

        return self





