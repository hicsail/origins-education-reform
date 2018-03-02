import argparse, json, os, math, csv
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
        self.g_max = math.inf
        self.g_min = 0

        self.check_year_lists()
        self.build_graph_dict()
        self.find_max_and_min()

    def check_year_lists(self):
        """
        Verify that all input corpora share a common year list.
        """

        year_lists = set()

        for corpus in self.corpora:
            year_lists.add(tuple(corpus.years))

        if len(year_lists) != 1:
            print("Warning: malformed year list inputs.")

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

    def create_plot(self):

        fig = plt.figure()
        ax1 = plt.subplot2grid((1, 1), (0, 0))






