import argparse, json, os, math, csv
import matplotlib.pyplot as plt
import numpy as np


class GraphFrequency:
    """
    Visualize NLP results. Takes an input list of FrequencyResults
    objects and produces a graph of them together.
    """

    def __init__(self, corpora: list):

        self.corpora = corpora
        self.graph_dict = {}
        self.year_list = []
        self.check_year_lists()
        self.build_graph_dict()

        print("Hi!")

    def check_year_lists(self):

        year_lists = set()

        for corpus in self.corpora:
            year_lists.add(tuple(corpus.years))

        if len(year_lists) != 1:
            print("Warning: malformed year list inputs.")

        self.year_list = self.corpora[0].years

    def build_graph_list(self, k, d):

        a = [0] * len(self.year_list)

        for i in range(len(self.year_list)):
            a[i] = d[self.year_list[i]][k]

        return a

    def build_graph_dict(self):

        # graph_dict[corpus.name][keyword] = <frequencies sorted by year>

        for corpus in self.corpora:

            c_res = corpus.d
            c_keys = c_res[self.year_list[0]].items()
            self.graph_dict[corpus.name] = {}

            for k in c_keys:
                self.graph_dict[corpus.name][k] = self.build_graph_list(k, c_res)

