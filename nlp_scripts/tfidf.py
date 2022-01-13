import common, json, argparse, os
from gensim import corpora, models
from shutil import copyfile


def filter_by_threshold(thresh, score):
    if score >= thresh:
        return True
    return False

def filter_tfidf(keywords, dictionary, in_dir, out_dir, tfidf_model, text_type, thresh):
    for subdir, dirs, files in os.walk(in_dir):
        for jf in files:
            if jf[0] == ".":
                continue
            text = extract_text(in_dir + jf, text_type)
            docbow = dictionary.doc2bow(text)
            for keyword in keywords:
                words = keyword.split("/")
                # abstract all this into another method, doing too much
                for w in words:
                    if w not in set(text):
                        continue
                    w_id = dictionary.token2id[w]
                    tfidf = tfidf_model[docbow]
                    for score in tfidf:
                        if score[0] != w_id:
                            continue
                        # check against threshold, copy if above
                        if filter_by_threshold(thresh, score[1]):
                            copied = True
                            copyfile(in_dir + jf, out_dir + keyword + '/' + jf)
                            # only want one copy, break to next keyword


def extract_text(jf, text_type):
    with open(jf, 'r', encoding='utf-8') as in_j:
        jsondata = json.load(in_j)
        text = jsondata[text_type]
    return text


def construct_dictionary_and_corpus(in_dir, text_type):
    dictionary = corpora.Dictionary()
    corpus = []
    for subdir, dirs, files in os.walk(in_dir):
        for jf in files:
            if jf[0] == ".":
                continue
            text = extract_text(in_dir + jf, text_type)
            dictionary.add_documents([text])
            corpus.append(dictionary.doc2bow(text))
    return dictionary, corpus

def build_out(out_dir):
    if out_dir is not None:
        # create / overwrite directory where results will be stored
        if not os.path.exists(out_dir):
            os.mkdir(out_dir)
        else:
            shutil.rmtree(out_dir)
            os.mkdir(out_dir)
    else:
        raise Exception("Please specify output directory.")

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i",
        help="Input directory path",
        action="store",
        required=True
    )
    parser.add_argument(
        "-o",
        help="Output directory",
        action="store",
        required=True
    )
    parser.add_argument(
        "-thresh",
        type=float,
        help="Minimum TF-IDF score to display",
        action="store",
        required=True
    )
    parser.add_argument(
        "-type",
        help="Text field to use in analysis",
        default="Words",
        action="store",
        required=True
    )
    parser.add_argument(
        "-k",
        help="List of keywords for analysis",
        action="store",
        required=True
    )

    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()

    key_list = common.build_key_list(args.k, False)
    build_out(args.o)
    common.build_subdirs(args.o, key_list, False)

    dictionary, corpus = construct_dictionary_and_corpus(args.i, args.type)

    # TODO: make this configurable
    '''
    dictionary.save('/tmp/dictionary.dict')
    corpora.MmCorpus.serialize('/tmp/corpus.mm', corpus)
    '''

    tfidf = models.TfidfModel(corpus)

    filter_tfidf(key_list, dictionary, args.i, args.o, tfidf, args.type, args.thresh)