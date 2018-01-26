import json, tqdm, nltk
from nlp.utils import *


class Frequency:
    def __init__(self, name, in_dir, text_type, keys, year_list):
        self.name = name
        self.in_dir = in_dir
        self.text_type = text_type
        self.key_list = self.build_keys(keys)
        self.year_list = year_list
        self.n = self.detect_n()

    def debug_str(self):
        return self.name \
               + ":" \
               + ", ".join("\'" + " ".join(k for k in keys) + "\'" for keys in self.key_list)

    def detect_n(self):
        """
        Detect value of n for word frequency.

        :return: integer
        """

        lengths = set()
        for k in self.key_list:
            lengths.add(len(k))

        assert(len(lengths) == 1)

        return lengths.pop()

    @staticmethod
    def build_keys(keys):
        """
        Build list of keyword tuples
        """

        return [tuple(k.split()) for k in keys.split('/')]

    def reduce_frequencies(self, freq_dict):
        """
        Reduce leaf values in frequency dicts to obtain average frequencies for each period / keyword pair
        """

        results = num_dict(self.year_list, self.key_list, 1)
        for year in self.year_list:
            if len(freq_dict[year]['TOTAL']) > 0:
                results[year]['TOTAL'] = \
                    sum(freq_dict[year]['TOTAL']) / len(freq_dict[year]['TOTAL'])
            for k in self.key_list:
                if len(freq_dict[year][k]) > 0:
                    results[year][k] = \
                        sum(freq_dict[year][k]) / len(freq_dict[year][k])
        return results

    def take_frequencies(self):
        """
        Construct dictionary that stores frequencies of each word across a corpus.
        """

        frequency_lists = list_dict(self.year_list, self.key_list, 1)
        print(self.in_dir)
        for subdir, dirs, files in os.walk(self.in_dir):
            print("Taking word counts for key list {}".format(self.key_list))
            for jsondoc in tqdm.tqdm(files):
                if jsondoc[0] != ".":
                    with open(self.in_dir + "/" + jsondoc, 'r', encoding='utf8') as in_file:
                        jsondata = json.load(in_file)
                        year = int(jsondata["Year Published"])
                        if self.year_list[0] <= year < self.year_list[-1]:
                            text = list(nltk.ngrams(jsondata[self.text_type], self.n))
                            target = determine_year(year, self.year_list)

                            total_words = len(list(text))
                            all_keys = 0

                            fdist = nltk.FreqDist(text)

                            for k in self.key_list:
                                all_keys += fdist[k]
                                frequency_lists[target][k].append(fdist[k] / total_words)

                            frequency_lists[target]['TOTAL'].append(all_keys / total_words)

        results = self.reduce_frequencies(frequency_lists)

        return results

