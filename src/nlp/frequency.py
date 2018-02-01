import json, tqdm, nltk, math
from src.utils import *
from src.results import *
from src.nlp import Corpus


class Frequency(Corpus):
    """
    Data structure for calculating word frequencies with respect
    to a list of year periods and (optionally) key words. Keywords
    can be either individual words or n-grams for any n, but must
    use a consistent value of n within a particular list.
    """

    def __init__(self, name: str, in_dir: str, text_type: str, year_list: list,
                 keys: [list, None]=None, stop_words: [list, None] = []):
        """ Initialize Frequency object. """

        super(Frequency, self).__init__(name, in_dir, text_type, year_list, keys, stop_words)

        self.frequency_record = None
        self.global_freq = None
        self.avg_freq = None
        self.variance = None

    def set_frequency_record(self):
        """
        Construct a dictionary that stores the
        frequencies of each word across a corpus.
        """

        if self.frequency_record is not None:
            return

        # TODO: convert to exception
        assert(self.key_list is not None)

        frequency_lists = list_dict(self.year_list, self.key_list, 1)
        n = self.detect_n()

        print("Taking word counts for key list {}".format(self.key_list))

        for subdir, dirs, files in os.walk(self.in_dir):
            for jsondoc in tqdm.tqdm(files):
                if jsondoc[0] != ".":

                    with open(self.in_dir + "/" + jsondoc, 'r', encoding='utf8') as in_file:

                        jsondata = json.load(in_file)
                        year = int(jsondata["Year Published"])

                        if self.year_list[0] <= year < self.year_list[-1]:

                            text = list(nltk.ngrams(jsondata[self.text_type], n))

                            for i in range(len(text) - 1, -1, -1):

                                # Delete empty strings and single characters
                                if text[i] in self.stop_words or len(text[i]) < 2:
                                    del text[i]

                            target = determine_year(year, self.year_list)

                            total_words = len(list(text))
                            all_keys = 0

                            fdist = nltk.FreqDist(text)

                            for k in self.key_list:

                                all_keys += fdist[k]
                                frequency_lists[target][k].append((fdist[k], total_words))

                            frequency_lists[target]['TOTAL'].append((all_keys, total_words))

        self.frequency_record = frequency_lists

    def take_freq(self):
        """
        Reduce leaf entries in frequency dicts to obtain
        global frequencies for each period / keyword pair
        """

        if self.global_freq is not None:
            return FrequencyResults(self.global_freq, 'Global')

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

        self.global_freq = results

        return FrequencyResults(results, 'Global frequency (%)')

    def take_average_freq(self):
        """
        Reduce leaf entries in frequency dicts to obtain
        average frequencies for each period / keyword pair.
        """

        if self.avg_freq is not None:
            return FrequencyResults(self.avg_freq, 'Average frequency')

        if self.frequency_record is None:
            self.set_frequency_record()

        freq = self.frequency_record

        results = num_dict(self.year_list, self.key_list, 1)

        for year in self.year_list:

            if len(freq[year]['TOTAL']) > 0:
                results[year]['TOTAL'] = sum(x for x, _ in freq[year]['TOTAL']) / len(freq[year]['TOTAL'])

            for k in self.key_list:

                if len(freq[year][k]) > 0:
                    results[year][k] = sum(x for x, _ in freq[year][k]) / len(freq[year][k])

        self.avg_freq = results

        return FrequencyResults(results, 'Average frequency')

    def take_variance(self):
        """
        Combine & reduce leaf entries in frequency and average frequency
        dicts to obtain the variance for each period / keyword pair.
        """

        if self.variance is not None:
            return FrequencyResults(self.variance, 'Variance')

        if self.frequency_record is None:
            self.set_frequency_record()

        if self.avg_freq is None:
            self.take_average_freq()

        freq = self.frequency_record
        avg = self.avg_freq

        results = num_dict(self.year_list, self.key_list, 1)

        for year in self.year_list:

            if len(freq[year]['TOTAL']) > 0:

                var = []
                for fr in freq[year]['TOTAL']:

                    v = math.pow(fr[0] - avg[year]['TOTAL'], 2)
                    var.append(v)

                results[year]['TOTAL'] = sum(var) / len(var)

            for k in self.key_list:

                if len(freq[year][k]) > 0:

                    var = []
                    for fr in freq[year][k]:

                        v = math.pow(fr[0] - avg[year][k], 2)
                        var.append(v)

                    results[year][k] = sum(var) / len(var)

        self.variance = results

        return FrequencyResults(results, 'Variance')

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
