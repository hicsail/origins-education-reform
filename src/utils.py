import os


class FrequencyResults:
    """ Data structure that stores word frequency results over a list of keywords. """

    def __init__(self, d: dict, name: [None, str]=None):
        """ Initialize FrequencyResults object. """

        self.d = d
        self.years = [y[0] for y in self.d.items()]
        self.name = name

    @staticmethod
    def build_keys(keys: list):
        """ Build list of keyword tuples. """

        return [tuple(k.split()) for k in keys]

    def write(self, out_path: str):
        """ Write contents of FrequencyResults object to file. """

        with open(out_path + '.txt', 'w') as t:
            print("Writing results to text file.")

            for i in range(len(self.years) - 1):
                t.write(
                    "________________\n"
                    "Period: {0} - {1}\n"
                    .format(str(self.years[i]), str(self.years[i+1]))
                    + "\n"
                )
                for k in self.d[self.years[i]].items():
                    if k[0] == 'TOTAL':
                        t.write(
                            "Frequency of all keywords for this period: {}%"
                            .format(str(k[1]))
                            + "\n"
                        )
                    else:
                        t.write(
                            "Frequency of \"{0}\" for this period: {1}%"
                            .format(" ".join(k[0]), str(k[1]))
                            + "\n"
                        )

    def display(self, keys: [None, list]=None):
        """ Display FrequencyResults in console. """

        if keys is not None:
            keys = self.build_keys(keys)
        else:
            keys = ['TOTAL']

        for i in range(len(self.years) - 1):
            print(
                "________________\n"
                "Period: {0} - {1}"
                .format(str(self.years[i]), str(self.years[i+1]))
                + "\n")
            for k in keys:
                if k == 'TOTAL':
                    print(
                        "Frequency of all keywords for this period: {}%"
                        .format(str(self.d[self.years[i]]['TOTAL']))
                        + "\n"
                    )
                else:
                    print(
                        "Frequency of \"{0}\" for this period: {1}%"
                        .format(" ".join(k), str(self.d[self.years[i]][k]))
                        + "\n"
                    )


class TopResults:
    """ Data structure that stores top word frequencies across a corpus. """

    def __init__(self, d: dict):
        self.d = d
        self.years = [y[0] for y in self.d.items()]

    def write(self, out_path: str):
        """ Write contents of FrequencyResults object to file. """

        with open(out_path + '.txt', 'w') as t:
            print("Writing results to text file.")

            for i in range(len(self.years) - 1):
                t.write(
                    "________________\n"
                    "Period: {0} - {1}"
                    .format(str(self.years[i]), str(self.years[i+1]))
                    + "\n"
                )
                t.write("Top words for this period: \n")
                for k in self.d[self.years[i]]:
                    t.write(
                        "\"{0}\": {1}%"
                        .format(" ".join(k[0]), str(k[1]))
                        + "\n"
                    )

    def display(self):
        """ Display TopResults in console. """

        for i in range(len(self.years) - 1):
            print(
                "________________\n"
                "Period: {0} - {1}"
                .format(str(self.years[i]), str(self.years[i+1]))
                + "\n")
            print("Top words for this period:")
            for k in self.d[self.years[i]]:
                print(
                    "\"{0}\": {1}%"
                    .format(" ".join(k[0]), str(k[1]))
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


def list_dict(year_list: list, keywords: [list, None]=None, nested: [None, int]=0):
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











