import json, tqdm, nltk
from src.utils import *


class KeywordFrequency:
    """
    Data structure for calculating word frequencies with
    respect to a list of keywords and year periods. Keywords
    can be either individual words or n-grams for any n, but
    must use a consistent value of n within a particular list.
    """

    def __init__(self, name: str, in_dir: str, text_type: str, year_list: list, keys: [list, None]=None):
        """ Initialize Frequency object. """

        self.name = name
        self.in_dir = in_dir
        self.text_type = text_type
        self.year_list = year_list
        if keys is not None:
            self.key_list = self.build_keys(keys)

        self.frequency_record = None

    def debug_str(self):
        """ Debug / identify individual Frequency objects. """

        return self.name \
               + ":" \
               + ", ".join("\'" + " ".join(k for k in keys) + "\'" for keys in self.key_list)

    def detect_n(self):
        """ Detect value of n for word frequency. """

        lengths = set()
        for k in self.key_list:
            lengths.add(len(k))

        assert(len(lengths) == 1)

        return lengths.pop()

    @staticmethod
    def build_keys(keys: list):
        """ Build list of keyword tuples. """

        return [tuple(k.split()) for k in keys]

    def set_frequency_record(self):
        """
        Construct a dictionary that stores the
        frequencies of each word across a corpus.
        """

        # TODO: change this to an exception
        assert(self.key_list is not None)

        frequency_lists = list_dict(self.year_list, self.key_list, 1)
        n = self.detect_n()

        for subdir, dirs, files in os.walk(self.in_dir):
            print("Taking word counts for key list {}".format(self.key_list))
            for jsondoc in tqdm.tqdm(files):
                if jsondoc[0] != ".":
                    with open(self.in_dir + "/" + jsondoc, 'r', encoding='utf8') as in_file:
                        jsondata = json.load(in_file)
                        year = int(jsondata["Year Published"])
                        if self.year_list[0] <= year < self.year_list[-1]:
                            text = list(nltk.ngrams(jsondata[self.text_type], n))
                            target = determine_year(year, self.year_list)

                            total_words = len(list(text))
                            all_keys = 0

                            fdist = nltk.FreqDist(text)

                            for k in self.key_list:
                                all_keys += fdist[k]
                                frequency_lists[target][k].append((fdist[k], total_words))

                            frequency_lists[target]['TOTAL'].append((all_keys, total_words))

        self.frequency_record = frequency_lists

    def take_frequencies(self):
        """
        Reduce leaf entries in frequency dicts to obtain
        average frequencies for each period / keyword pair
        """

        if self.frequency_record is None:
            self.set_frequency_record()

        freq = self.frequency_record

        results = num_dict(self.year_list, self.key_list, 1)
        for year in self.year_list:

            if len(freq[year]['TOTAL']) > 0:
                w_freq = sum(x for x, _ in freq[year]['TOTAL'])
                total = sum(y for _, y in freq[year]['TOTAL'])
                results[year]['TOTAL'] = w_freq / total

            for k in self.key_list:

                if len(freq[year][k]) > 0:
                    w_freq = sum(x for x, _ in freq[year][k])
                    total = sum(y for _, y in freq[year][k])
                    results[year][k] = w_freq / total

        return FrequencyResults(results)

    @staticmethod
    def _top_n(fdist: nltk.FreqDist, num: int, total_words: dict):
        """
        Helper to top_n. Returns a list of lists, with each
        list representing the top n words for a given period.
        """

        keys = []
        top = fdist.most_common(num)

        for tup in top:
            keys.append((tup[0], round((tup[1] / total_words) * 100, 4)))

        return keys

    def top_n(self, num: int, n: int=1):
        """
        Construct a dictionary that stores the top
        < num > words per period across a corpus.
        """

        fdists = num_dict(self.year_list)
        num_words = num_dict(self.year_list)
        n_words = list_dict(self.year_list)
        print("Calculating top {0} words per period".format(str(num)))

        for subdir, dirs, files in os.walk(self.in_dir):
            for jsondoc in tqdm.tqdm(files):
                if jsondoc[0] != ".":
                    with open(self.in_dir + "/" + jsondoc, 'r', encoding='utf8') as in_file:
                        jsondata = json.load(in_file)
                        year = int(jsondata["Year Published"])
                        if self.year_list[0] <= year < self.year_list[-1]:
                            text = list(nltk.ngrams(jsondata[self.text_type], n))
                            target = determine_year(year, self.year_list)

                            total_words = len(list(text))
                            num_words[target] += total_words
                            fdist = nltk.FreqDist(text)

                            if fdists[target] == 0:
                                fdists[target] = fdist
                            else:
                                fdists[target] |= fdist

        for year in self.year_list[:-1]:
            if len(fdists[year]) >= num:
                n_words[year].extend(self._top_n(fdists[year], num, num_words[year]))
            else:
                n_words[year].extend(self._top_n(fdists[year], len(fdists[year]), num_words[year]))

        return TopResults(n_words)


if __name__ == "__main__":

    f = KeywordFrequency(
        'test',
        '/Users/ben/Desktop/work/nlp/british',
        'Filtered Text',
        [1700, 1720, 1740],
        ['two']
    )

    res = f.top_n(5)
    # res2 = f.take_frequencies()
    res.display()
    res.write('/Users/ben/Desktop/results')

    print("Done")
