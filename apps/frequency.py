from src import corpus

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

    f.take_freq().display()

