from src import corpus

if __name__ == '__main__':

    c = corpus.Corpus(
        'test',
        '/Users/ben/Desktop/work/nlp/british/',
    )

    f = c.tf_idf(
        'freq',
        [1700, 1720, 1740],
        ['miss', 'upon'],
        'Filtered Text'
    )

    f.top_n(
        'jonathan',
        10
    ).display()

