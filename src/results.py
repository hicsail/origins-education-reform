

class FrequencyResults:
    """ Data structure that stores word frequency results over a list of keywords. """

    def __init__(self, d: dict, f_type: str, name: [None, str]=None):
        """ Initialize FrequencyResults object. """

        self.d = d
        self.years = [y[0] for y in self.d.items()]
        self.name = name
        self.f_type = f_type

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
                )
                for k in self.d[self.years[i]].items():
                    if k[0] == 'TOTAL':
                        t.write(
                            "{0} of all keywords taken together for this period: {1}\n"
                            .format(self.f_type, str(k[1]))
                        )
                    else:
                        t.write(
                            "{0} of \"{1}\" for this period: {2}\n"
                            .format(self.f_type, " ".join(k[0]), str(k[1]))
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
                "Period: {0} - {1}\n"
                .format(str(self.years[i]), str(self.years[i+1]))
            )
            for k in keys:
                if k == 'TOTAL':
                    print(
                        "{0} of all keywords taken together for this period: {1}"
                        .format(self.f_type, str(self.d[self.years[i]]['TOTAL']))
                        + "\n"
                    )
                else:
                    print(
                        "{0} of \"{1}\" for this period: {2}\n"
                        .format(self.f_type, " ".join(k), str(self.d[self.years[i]][k]))
                    )


class TopResults:
    """ Data structure that stores top word frequencies across a corpus. """

    def __init__(self, d: dict):
        self.d = d
        self.years = [y[0] for y in self.d.items()]

    def write(self, out_path: str):
        """ Write contents of Frequency object to file. """

        with open(out_path + '.txt', 'w') as t:
            print("Writing results to text file.")

            for i in range(len(self.years) - 1):
                t.write(
                    "________________\n"
                    "Period: {0} - {1}\n"
                    .format(str(self.years[i]), str(self.years[i+1]))
                )
                t.write("Top words for this period: \n")
                for k in self.d[self.years[i]]:
                    t.write(
                        "\"{0}\": {1}%\n"
                        .format(" ".join(k[0]), str(k[1]))
                    )

    def display(self):
        """ Display TopResults in console. """

        for i in range(len(self.years) - 1):
            print(
                "________________\n"
                "Period: {0} - {1}\n"
                .format(str(self.years[i]), str(self.years[i+1]))
            )
            print("Top words for this period:")
            for k in self.d[self.years[i]]:
                print(
                    "\"{0}\": {1}%"
                    .format(" ".join(k[0]), str(k[1]))
                )


class TfidfResults:
    """ Data structure that stores documents with the highest TF-IDF score per period. """

    def __init__(self, d: dict, keyword: str, name: [None, str]=None):

        self.d = d
        self.years = [y[0] for y in self.d.items()]
        self.keyword = keyword
        self.name = name

    def write(self, out_path: str):
        """ Write contents of Tfidf object to file. """

        with open(out_path + '.txt', 'w') as t:
            print("Writing results to text file.")

            for i in range(len(self.years) - 1):
                t.write(
                    "________________\n"
                    "Period: {0} - {1}\n"
                    .format(str(self.years[i]), str(self.years[i+1]))
                )
                t.write(
                    "Documents with the highest TF-IDF score for \'{0}\' in this period: \n"
                    .format(self.keyword)
                )
                for k in self.d[self.years[i]]:
                    t.write(
                        "\"{0}\": {1}%\n"
                        .format(k[0], str(k[1]))
                    )

    def display(self):
        """ Display Tfidf results in console. """

        for i in range(len(self.years) - 1):
            print(
                "________________\n"
                "Period: {0} - {1}\n"
                .format(str(self.years[i]), str(self.years[i+1]))
            )
            print("Documents with the highest TF-IDF score for \'{0}\' in this period: \n"
                  .format(self.keyword))
            for k in self.d[self.years[i]]:
                print(
                    "\"{0}\": {1}%"
                    .format(k[0], str(k[1]))
                )
