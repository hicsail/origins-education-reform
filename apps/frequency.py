from src import corpus, graph

if __name__ == '__main__':

    c = corpus.Corpus(
        'test',
        '/Users/ben/Desktop/work/nlp/british/',
    )

    e = c.variance(
        'var',
        [1700, 1720, 1740],
        ['miss', 'upon'],
        'Filtered Text'
    )

    e.display()

    g = graph.GraphFrequency([e]).create_plot().show()
