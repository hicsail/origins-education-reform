from src import corpus, graph

if __name__ == '__main__':

    c = corpus.Corpus(
        'test',
        '/Users/ben/Desktop/work/nlp/british/',
    )

    f = c.frequency(
        'freq',
        [1700, 1720, 1740],
        ['miss', 'upon'],
        'Filtered Text'
    )

    f.display()

    g = c.avg_frequency(
        'avgfreq',
        [1700, 1720, 1740],
        ['miss', 'upon'],
        'Filtered Text'
    )

    g.display()

    e = c.variance(
        'var',
        [1700, 1720, 1740],
        ['miss', 'upon'],
        'Filtered Text'
    )

    e.display()

    h = c.top_n(
        'top',
        [1700, 1720, 1740],
        'Filtered Text'
    )

    h.display()

    # g = graph.GraphFrequency([f])
