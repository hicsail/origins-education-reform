import argparse, sys
from nltk.stem.snowball import SnowballStemmer

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-words",
        help="Words to stem",
        nargs="+",
        action="store",
        required=True
    )
    parser.add_argument(
        "-language",
        help="Language of words",
        action="store",
        required=True
    )

    args = parser.parse_args()
    return args

if __name__ == '__main__':
    args = parse_args()

    stemmer = SnowballStemmer(args.language)
    for word_list in args.words:
        for word in word_list.split():
            print(stemmer.stem(word))