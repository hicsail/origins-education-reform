import argparse, os
from nltk.stem.snowball import SnowballStemmer


#                   *** StemChecker.py ***
# We were having trouble predicting how the SnowballStemmer would stem
# individual words (e.g. 'liberty' to 'liberti', 'capital' to 'capit', etc.).
# So, this is simple script that just takes a list of words and produces each 
# word's corresponding stem. Output is printed to console.
#


# returns list of tuples made up of each word and it's corresponding stem
def stemText(word_list, language):
    # Init stemmer & array to store stemmed words
    stemmer = SnowballStemmer(language)
    stemmed = []
    for word in word_list:
        word.encode('utf-8')
        stemmed.append((word, stemmer.stem(word)))
    return stemmed


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-words", help="list of words to stem", action="store")
    parser.add_argument("-language", help="desired language", action="store")

    def fail(msg):
        print(msg)
        os._exit(1)

    try:
        args = parser.parse_args()
    except IOError:
        fail("IO Error, please enter valid input.")
    
    # lowercase list of words to be stemmed
    word_list = args.words.lower().split()
    # convert desired language to lowercase
    language = args.language.lower()
    # list of word/stemmed tuples
    word_tups = stemText(word_list, language)
    # print to console
    for tup in word_tups:
        print("Word \"{0}\" stems to: \"{1}\"".format(tup[0], tup[1]))

if __name__ == '__main__':
    main()
