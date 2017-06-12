import common, json, argparse, os
from gensim import corpora
from nltk.corpus import stopwords
from six import iteritems


def filtered_ids(stopwords, dictionary):
    stop_ids = [dictionary.token2id[stopword] for stopword in stopwords
                if stopword in dictionary.token2id]
    once_ids = [tokenid for tokenid, docfreq in iteritems(dictionary.dfs) if docfreq == 1]
    return stop_ids + once_ids


def extract_text(jf, text_type):
    with open(jf, 'r', encoding='utf-8') as in_j:
        jsondata = json.load(in_j)
        text = jsondata[text_type]
    return text


def construct_dictionary(in_dir, text_type):
    dictionary = corpora.Dictionary()
    for subdir, dirs, files in os.walk(in_dir):
        for jf in files:
            if jf[0] != ".":
                dictionary.add_documents([extract_text(in_dir + jf, text_type)])
    return dictionary


def determine_text_type(text_type):
    if text_type == 'full':
        text = "Full Text"
    elif text_type == 'stemmed':
        text = "Full Text Stemmed"
    elif text_type == 'filtered stemmed':
        text = 'Filtered Text Stemmed'
    else:
        text = text_type
    return text


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", metavar="in-directory", action="store", help="input directory argument")
    parser.add_argument("-o", help="output directory", action="store")
    parser.add_argument("-thresh", help="tf-idf threshold", action="store")
    parser.add_argument("-type", help="text field from json doc", action="store")
    parser.add_argument("-lang", help="language", action="store")

    try:
        args = parser.parse_args()
    except IOError:
        pass

    if args.i is None:
        common.fail("Please specify input (-i) directory.")
    if args.type is None:
        text_type = 'Filtered Text'
    else:
        text_type = determine_text_type(args.type.lower())
    if args.lang is None:
        language = 'english'
    else:
        language = args.lang.lower()

    common.build_out(args.o)
    stoplist = set(stopwords.words(language))

    dictionary = construct_dictionary(args.i, text_type)
    dictionary.filter_tokens(filtered_ids(stoplist, dictionary)).compactify()

    # TODO: save dictionary to disk for later use
    # TODO: filter docs w/r/t keyword / threshold
    # TODO: write filtered docs to disk or just save file IDs?

if __name__ == '__main__':
    main()

