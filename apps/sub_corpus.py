from src import corpus

if __name__ == '__main__':

    c = corpus.Corpus(
        'test',
        '/Users/ben/Desktop/work/nlp/british/',
    )

    s = c.build_sub_corpus(
        'sub',
        '/Users/ben/Desktop/sub_corpus',
        ['jonathan', 'lady'],
        'Filtered Text',
        40,
        [1700, 1800]
    )