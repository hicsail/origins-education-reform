import common, json, argparse, os
from gensim import corpora


def extract_text(jf, text_type):
    jsondata = json.load(jf)
    text = jsondata[text_type]
    return text


# TODO: add_documents or create new dict and merge?
def construct_dictionary(in_dir, text_type):
    dictionary = corpora.Dictionary()
    for subdir, dirs, files in os.walk(in_dir):
        for jf in files:
            if jf[0] != ".":
                dictionary.add_documents(extract_text(jf, text_type))
    return ''


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
    parser.add_argument("type", help="text field from json doc", action="store")

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

    common.build_out(args.o)


if __name__ == '__main__':
    main()

