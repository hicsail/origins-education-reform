from src import corpus
from src.diff_prop import DiffProportions

if __name__ == '__main__':

    c = corpus.Corpus(
        'test',
        '/Users/ben/Desktop/work/nlp/british/',
    )

    # name: str, text_type: str, key_list: list, binary: bool=False
    rf = c.raw_frequency('test', 'Filtered Text', ['miss', 'upon'], binary=True)

    rf2 = c.raw_frequency('test2', 'Filtered Text', ['swift', 'govern'], binary=True)

    dp = DiffProportions('dp', [rf, rf2], [1800, 1820, 1840]).take_difference().display()
