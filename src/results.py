import re
from src.utils import *


class Results:
    """ Base class for all Results objects. """

    def __init__(self, d: dict):
        """ Initialize Results object. """

        self.d = d
        self.years = [y[0] for y in self.d.items()]


class FrequencyResults(Results):
    """ Data structure that stores word frequency results over a list of keywords. """

    def __init__(self, d: dict, f_type: str, name: [None, str]='Frequency'):
        """ Initialize FrequencyResults object. """

        super(FrequencyResults, self).__init__(d)

        self.name = name
        self.f_type = f_type

    def debug_str(self):
        print("FrequencyResults object: \n\t - name: {0} \n\t - stores: {1}"
              .format(self.name, self.f_type)
              )

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
            keys = build_keys(keys)
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


class TopResults(Results):
    """ Data structure that stores top word frequencies across a corpus. """

    def __init__(self, d: dict, name: [None, str]='Top Frequencies'):
        """ Initialize TopResults object. """

        super(TopResults, self).__init__(d)

        self.name = name

    def debug_str(self):
        print("TopResults object: \n\t - name: {0}"
              .format(self.name)
              )

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


class TfidfResults(Results):
    """ Data structure that stores documents ranked by TF-IDF score for a keyword per period. """

    def __init__(self, d: dict, keyword: str, name: [None, str]='TF-IDF'):
        """ Initialize TfidfResults object. """

        super(TfidfResults, self).__init__(d)

        self.keyword = keyword
        self.name = name

    def debug_str(self):
        print("TfidfResults object: \n\t - name: {0} \n\t - keyword: {1}"
              .format(self.name, self.keyword)
              )

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


class TopicResults(Results):

    def __init__(self, d: dict, name: [None, str]='LDA Model'):

        super(TopicResults, self).__init__(d)

        self.name = name

    def debug_str(self):
        print("LdaResults object: \n\t - {0}"
              .format(self.name)
              )

    def write(self, out_path: str, num_topics: int=10,
              num_words: int=10, weights: bool=False):
        """ Write contents of LdaResults object to file. """

        def _filter_topic(t):
            filtered = re.split('\W[0-9]*', str(t))

            for k in range(len(filtered) - 1, -1, -1):
                if filtered[k] == "" or filtered[k] == "None":
                    del filtered[k]
                else:
                    filtered[k] = filtered[k].lower()
            return ", ".join(filtered)

        def _filter_topic_weights(t):
            filtered = str(t[1]).split('+')

            for k in range(len(filtered) - 1, -1, -1):
                if filtered[k] == "" or filtered[k] == "None":
                    del filtered[k]
                else:
                    filtered[k] = filtered[k].split('*')

            res = []
            for k in filtered:
                res.append(
                    "{0} ({1})".format(k[1].strip(), k[0].strip())
                )

            return ", ".join(res)

        with open(out_path, 'w') as t:
            print("Writing results to file.")

            for i in range(len(self.years) - 1):
                t.write(
                    "________________\n"
                    "Period: {0} - {1}\n"
                    .format(str(self.years[i]), str(self.years[i+1]))
                )
                topics = self.d[self.years[i]]\
                    .show_topics(num_topics=num_topics, num_words=num_words)
                idx = 0
                for topic in topics:
                    if not weights:
                        top = _filter_topic(topic)
                        t.write("Topic {0}: {1}\n"
                                .format(str(idx), top)
                                )
                        idx += 1
                    else:
                        top = _filter_topic_weights(topic)
                        t.write("Topic {0}: {1}\n"
                                .format(str(idx), top))
                        idx += 1

