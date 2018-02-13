from src import corpus

if __name__ == '__main__':

    c = corpus.Corpus(
        'test',
        '/Users/ben/Desktop/work/nlp/british/',
    )

    t = c.topic_model(
        'lda',
        [1700, 1720, 1740],
        'Filtered Text'
    )

    lda = t.lda_model().write(
        '/Users/ben/Desktop/test_out.txt'
    )
