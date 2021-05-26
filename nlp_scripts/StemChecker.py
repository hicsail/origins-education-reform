import sys
from nltk.stem.snowball import SnowballStemmer

if __name__ == '__main__':
    language = input("Input language: ").strip().lower()
    stemmer = SnowballStemmer(language)
    try:
        while True:
            word = input("Enter a word or press Ctrl+C to exit: ")
            if " " in word:
                print("Not a word!")
                continue
            print(stemmer.stem(word))
    except KeyboardInterrupt:
        sys.exit()
