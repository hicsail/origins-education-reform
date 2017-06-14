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
            if jf[0] != ".":
                text = extract_text(in_dir + jf, text_type)
                docbow = dictionary.doc2bow(text)
                for keyword in keywords:
                    words = keyword.split("/")
                    # abstract all this into another method, doing too much
                    for w in words:
                        if w in set(text):
                            w_id = dictionary.token2id[w]
                            tfidf = tfidf_model[docbow]
                            copied = False
                            if not copied:
                                for score in tfidf:
                                    if score[0] == w_id:
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
            if jf[0] != ".":
                text = extract_text(in_dir + jf, text_type)
                dictionary.add_documents([text])
                corpus.append(dictionary.doc2bow(text))
    return [dictionary, corpus]


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


def args_setup(in_dir, keys, out_dir, text_type, threshold):
    if in_dir is None:
        common.fail("Please specify input (-i) directory.")
    if keys is None:
        common.fail("Please specify keywords (-k)")
    else:
        # TODO: make bigrams configurable in future if needed
        key_list = common.build_key_list(keys, False)
    if out_dir is None:
        common.fail("Please specify output (-o) directory.")
    else:
        common.build_out(out_dir)
        common.build_subdirs(out_dir, key_list, False)
    if text_type is None:
        text_type = 'Filtered Text Stemmed'
    else:
        text_type = determine_text_type(text_type.lower())
    if threshold is None:
        common.fail("Please specify TF-IDF threshold argument (-thresh")
    else:
        thresh = float(threshold)
    return [key_list, text_type, thresh]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", metavar="in-directory", action="store", help="input directory argument")
    parser.add_argument("-o", help="output directory", action="store")
    parser.add_argument("-thresh", help="tf-idf threshold", action="store")
    parser.add_argument("-type", help="text field from json doc", action="store")
    parser.add_argument("-k", help="keywords", action="store")

    try:
        args = parser.parse_args()
    except IOError:
        pass

    thresh = args.thresh.strip('"').strip("'")

    in_args = args_setup(args.i, args.k, args.o, args.type, thresh)
    key_list, text_type, thresh = in_args[0], in_args[1], in_args[2]

    model_params = construct_dictionary_and_corpus(args.i, text_type)
    dictionary, corpus = model_params[0], model_params[1]
    # TODO: make this configurable
    '''
    dictionary.save('/tmp/dictionary.dict')
    corpora.MmCorpus.serialize('/tmp/corpus.mm', corpus)
    '''

    tfidf = models.TfidfModel(corpus)

    filter_tfidf(key_list, dictionary, args.i, args.o, tfidf, text_type, thresh)

if __name__ == '__main__':
    main()

