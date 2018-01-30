import os


class Results:
    def __init__(self, d: dict):
        self.d = d

    def write(self, out_path):
        with open(out_path + '.txt', 'w') as t:
            print("Writing results to text file.")

            years = [y[0] for y in self.d.items()]

            for i in range(len(years) - 1):
                t.write(
                    "Period: {0} - {1}"
                    .format(str(years[i]), str(years[i+1])) + "\n"
                )
                for k in self.d[years[i]].items():
                    if k[0] == 'TOTAL':
                        t.write(
                            "Frequency of all keywords for this period: {} %"
                            .format(str(k[1])) + "\n"
                        )
                    else:
                        t.write(
                            "Frequency of \"{0}\" for this period: {1} %"
                            .format(" ".join(k[0]), str(k[1])) + "\n"
                        )


def _fail(msg):
    """ Generic fail method for debugging. """

    print(msg)
    os._exit(1)


def num_dict(year_list, keywords=None, nested=0):
    """ Build empty dictionary with integers at leaf entries. """

    results = {}
    for year in year_list:
        if nested == 0:
            results[year] = 0
        elif nested == 1:
            results[year] = {}
            results[year]['TOTAL'] = 0
            for keyword in keywords:
                results[year][keyword] = 0
        else:
            _fail('Shouldn\'t be able to get here.')
    return results


def list_dict(year_list, keywords=None, nested=0):
    """ Build empty dictionary with lists at leaf entries. """

    results = {}
    for year in year_list:
        if nested == 0:
            results[year] = []
        elif nested == 1:
            results[year] = {}
            for keyword in keywords:
                results[year]['TOTAL'] = []
                results[year][keyword] = []
        else:
            _fail('Shouldn\'t be able to get here.')
    return results


def determine_year(year, year_list):
    """
    Given a year and list of year periods,
    return which period that year falls into.
    """

    for i in (range(len(year_list[:-1]))):
        if year_list[i] <= year < year_list[i + 1]:
            return year_list[i]
    _fail("{} is not in range".format(year))











