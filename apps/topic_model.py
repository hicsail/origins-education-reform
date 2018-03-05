from src import corpus

if __name__ == '__main__':

    c = corpus.Corpus(
        'test',
        '/Users/ben/Desktop/work/nlp/british/',
    )

    t = c.lsi_model(
        'lsi',
        [1700, 1720, 1740],
        'Filtered Text'
    ).write(
        '/Users/ben/Desktop/test_out.txt'
    )
