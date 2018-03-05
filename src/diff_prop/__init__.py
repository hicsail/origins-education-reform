import statsmodels.api
import scipy.stats
from src.utils import *
from src.results import DiffPropResults


class DiffProportions:
    """
    Measure difference in proportions between two corpora.
    """

    def __init__(self, name: str, corpora: list, year_list: list):

        self.name = name
        self.corpora = corpora
        self.year_list = year_list
        self.binary = False

        self.check_binary()
        self.check_corpora()

    def check_binary(self):
        """
        Determine whether input corpora track binary,
        and ensure that the trackings match.
        """

        types = set()

        for corpus in self.corpora:
            types.add(corpus.binary)

        assert(len(types) == 1)

        self.binary = types.pop()

    def check_corpora(self):
        """
        Ensure that only two corpora have been passed.
        """

        assert(len(self.corpora) == 2)

    def _build_samples(self, corpus):
        """
        Build a dictionary of samples data for each corpus.
        """

        p = num_dict(self.year_list)
        n = num_dict(self.year_list)

        freq = corpus.freq_dict

        for doc in freq.keys():

            year = freq[doc]['Year Published']

            if self.year_list[0] < year < self.year_list[-1]:
                target = determine_year(year, self.year_list)
                key_records = freq[doc]['Frequencies']

                if self.binary:
                    n[target] += 1

                    for k in key_records:

                        if key_records[k] == 1:
                            p[target] += 1
                            break

                else:
                    n[target] += freq[doc]['Text Length']

                    for k in key_records:
                        p[target] += key_records[k]

        return p, n

    @staticmethod
    def diff_props_test(k1, n1, k2, n2):
        """
        Take difference of proportions
        Documentation:
        http://statsmodels.sourceforge.net/devel/generated/statsmodels.stats.proportion.proportions_ztest.html
        """

        (z, p_value) = statsmodels.api.stats.proportions_ztest(
            [k1, k2], [n1, n2], alternative='two-sided', prop_var=False
        )
        return [z, p_value]

    def take_difference(self):
        """
        Main method that takes difference in proportions between two corpora.
        """

        sample_records = {}

        names = [corpus.name for corpus in self.corpora]

        for corpus in self.corpora:
            sample_records[corpus.name] = self._build_samples(corpus)

        x1, n1 = sample_records[names[0]][0], sample_records[names[0]][1]
        x2, n2 = sample_records[names[1]][0], sample_records[names[1]][1]

        critical = scipy.stats.norm.ppf(1-(0.05/2))

        diff_props = list_dict(self.year_list)
        diff_props['Critical'] = critical

        for year in self.year_list[:-1]:
            vals = self.diff_props_test(x1[year], n1[year], x2[year], n2[year])
            z, p = vals[0], vals[1]
            sig = scipy.stats.norm.cdf(z)
            diff_props[year] = [z, p, sig]

        return DiffPropResults(diff_props, self.year_list)
