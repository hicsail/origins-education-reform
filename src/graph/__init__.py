import math
import matplotlib.pyplot as plt
import numpy as np


class GraphFrequency:
    """
    Visualize NLP results. Takes an input list of FrequencyResults
    objects and produces a graph of them together.
    """

    def __init__(self, corpora: list, title: str='Frequency Graph'):

        self.corpora = corpora
        self.title = title
        self.graph_dict = {}
        self.year_list = []
        self.g_max = 0
        self.g_min = math.inf
        self.plt = None

    def results_type(self):

        f_types = set()

        for corpus in self.corpora:
            f_types.add(corpus.f_type)

        if len(f_types) != 1:
            print("Warning: mismatched frequency types across corpora.\n")

        return self.corpora[0].f_type

    def check_year_lists(self):
        """
        Verify that all input corpora share a common year list.
        """

        year_lists = set()

        for corpus in self.corpora:
            year_lists.add(tuple(corpus.years))

        if len(year_lists) != 1:
            print("Warning: malformed year list inputs.\n")

        self.year_list = self.corpora[0].years

    def _build_graph_list(self, k, d):
        """
        Build a list of values to be graphed for a given keyword.
        """

        a = [0] * len(self.year_list)

        for i in range(len(self.year_list)):
            a[i] = d[self.year_list[i]][k]

        return a

    def build_graph_dict(self):
        """
        Traverse each corpus' frequency dictionaries and populate
        dictionary of keyword / value mappings to be graphed.
        """

        for corpus in self.corpora:

            c_res = corpus.d
            c_keys = [k[0] for k in c_res[self.year_list[0]].items()]

            self.graph_dict[corpus.name] = {}

            for k in c_keys:
                self.graph_dict[corpus.name][k] = self._build_graph_list(k, c_res)

    def find_max_and_min(self):
        """
        Traverse dict of frequency values and return min/max.
        """

        for c in self.graph_dict:
            for k in self.graph_dict[c]:
                for i in range(len(self.graph_dict[c][k])):
                    if self.graph_dict[c][k][i] > self.g_max:
                        self.g_max = self.graph_dict[c][k][i]
                    if self.graph_dict[c][k][i] < self.g_min:
                        self.g_min = self.graph_dict[c][k][i]

    def _generate_labels(self):

        labels = []
        for i in range(len(self.year_list) - 1):
            start = str(self.year_list[i])
            end = str(self.year_list[i + 1])
            labels.append("{0}-{1}".format(start, end))

        return labels

    def create_plot(self, x_label: str='Period', y_label: [str, None]=None,
                    title: [str, None]=None, bar: bool=True, bar_width: int=5,
                    leg_size: int=10):

        self.check_year_lists()
        self.build_graph_dict()
        self.find_max_and_min()

        ax1 = plt.subplot2grid((1, 1), (0, 0))

        plt.xlabel(x_label)

        if y_label is None:
            y_label = self.results_type()
            plt.ylabel(y_label)
        else:
            plt.ylabel(y_label)

        if title is None:
            plt.title(self.title)
        else:
            plt.title(title)

        index = np.array(sorted(self.year_list))
        plt.xticks(index, self._generate_labels())

        for label in ax1.xaxis.get_ticklabels():
            label.set_rotation(-25)
            label.set_size(7)

        if bar:
            i = 0
            for f in self.graph_dict:
                for k in self.graph_dict[f]:

                    ax1.bar(
                        index + (5 * i) + bar_width, self.graph_dict[f][k],
                        bar_width, alpha=.8,  color=np.random.rand(1, 3),
                        label="{0}: {1}".format(f, ' '.join(k) if isinstance(k, tuple) else k)
                    )
                    i += 1
            ax1.axis(
                [self.year_list[0], self.year_list[len(self.year_list) - 1], float(self.g_min), float(self.g_max)]
            )

        else:
            for f in self.graph_dict:
                for k in self.graph_dict[f]:

                    ax1.plot(index, self.graph_dict[f][k],
                             label="{0}: {1}".format(f, ' '.join(k) if isinstance(k, tuple) else k)
                             )
            ax1.axis(
                [self.year_list[0], self.year_list[len(self.year_list) - 2], float(self.g_min), float(self.g_max)]
            )

        leg = ax1.legend(prop={'size': leg_size})
        leg.get_frame().set_alpha(0.1)

        self.plt = plt

        return self

    def show(self):

        self.plt.show()

    def save(self, out_path: str):
        try:
            self.plt.savefig(out_path)
        except ValueError:
            print("Unsupported file format. \n"
                  "Please use one of the following: eps, pdf, pgf, png, ps, raw, rgba, svg, svgz")


