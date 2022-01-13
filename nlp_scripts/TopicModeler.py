import gensim, os, argparse, json, collections, re, nltk, numpy, tqdm
import common


# build list of keywords
def build_key_list(directory):
    key_list = []
    for dirs, subdirs, files in os.walk(directory):
        for subdir in subdirs:
            key_list.append(subdir)
    return key_list


# separate year / keyword pairs into lists of texts. this dictionary is used in
# conjunction with the build_frequency_dict function to yield a dictionary of
# 'bag of words' representations of each individual document.
def init_sent_doc_dict(input_dir, key_list, year_list, stopwords, min_year, max_year, text_type):
    doc_dict = common.build_dict_of_lists(year_list, key_list)
    for dirs, subdirs, files in os.walk(input_dir):
        # 'subdir' corresponds to each keyword
        print("Building volumes dictionary.")
        for subdir in tqdm.tqdm(subdirs):
            for folders, subfolders, file in os.walk(dirs + "/" + subdir):
                for jsondoc in file:
                    if jsondoc[0] == ".":
                        continue
                    with open(dirs + "/" + subdir + "/" + jsondoc, 'r', encoding='utf8') as inpt:
                        jsondata = json.load(inpt)
                        text = jsondata[text_type]
                        # remove stopwords
                        for i in range(len(text) - 1, -1, -1):
                            # Delete empty strings
                            if text[i] in stopwords or len(text[i]) < 2:
                                del text[i]
                        year = int(jsondata["Year"])
                        # check to make sure it's within range specified by user
                        if year < min_year or year >= max_year:
                            continue
                        target = common.determine_year(year, year_list)
                        try:
                            doc_dict[target][subdir].append(text)
                        except KeyError:
                            pass
    return doc_dict


# TODO could I just do this all in place - i.e. without having to store the whole corpus in memory first?
# yields word frequency for each document read in. used with init_sent_doc_dict
# to construct the 'bag of words' representation for each document.
def build_frequency_dict(doc_dict, key_list, year_list):
    dictionary = common.build_dict_of_dicts(year_list, key_list)
    print("Building bag-of-words dictionary.")
    for year in tqdm.tqdm(year_list):
        for key in key_list:
            frequency = collections.defaultdict(int)
            for doc in doc_dict[year][key]:
                for token in doc:
                    frequency[token] += 1
            texts = [[token for token in doc if frequency[token] > 1]
                     for doc in doc_dict[year][key]]
            dictionary[year][key] = gensim.corpora.Dictionary(texts)
    return dictionary


# declare / add to set of stopwords
def build_ignore_list(path_to_file, language):
    stopwords = set(nltk.corpus.stopwords.words(language))
    with open(path_to_file, 'r', encoding='utf-8') as ignored_list:
        jsondata = json.load(ignored_list)
        # load different categories, add tokens to stopwords set
        try:
            general = jsondata["General"]
            names = jsondata["Names"]
            nonsense = jsondata["Nonsense"]
            verbs = jsondata["Verbs"]
            adjectives = jsondata["Adjectives"]
            pronouns = jsondata["Pronouns"]
            nouns = jsondata["Nouns"]
            for noun in nouns:
                stopwords.add(noun)
            for adjective in adjectives:
                stopwords.add(adjective)
            for pronoun in pronouns:
                stopwords.add(pronoun)
            for verb in verbs:
                stopwords.add(verb)
            for word in nonsense:
                stopwords.add(word)
            for word in general:
                stopwords.add(word)
            for name in names:
                stopwords.add(name)
        # in case cathie is using old ignore list json format
        except KeyError:
            ig = jsondata['Ignored']
            for wd in ig:
                stopwords.add(wd)
    return stopwords

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i",
        help="Input directory path",
        action="store",
        required=True
    )
    parser.add_argument(
        "-txt",
        help="Text output filename",
        action="store",
        required=True
    )
    parser.add_argument(
        "-num_topics",
        type=int,
        help="Number of topics to display",
        default=10,
        action="store",
        required=True
    )
    parser.add_argument(
        "-num_words",
        type=int,
        help="Number of words per topic",
        default=10,
        action="store"
    )
    parser.add_argument(
        "-weights",
        help="Set to display topic weights",
        action="store_true"
    )
    parser.add_argument(
        "-lang",
        help="Input text language",
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
        "-ignore",
        help="Path to JSON file with stopwords",
        action="store"
    )
    parser.add_argument(
        "-y",
        help="Start year, end year, and year increment for grouping texts",
        action="store",
        required=True
    )
    parser.add_argument(
        "-p",
        help="Set to analyze a single period",
        action="store_true"
    )
    parser.add_argument(
        "-lsi",
        help="Set to use LSI for topic modelling",
        default=False,
        action="store_true"
    )
    parser.add_argument(
        "-include_keys",
        help="Set to show keywords in topics",
        action="store_true"
    )
    parser.add_argument(
        "-passes",
        type=int,
        help="Number of topic modelling passes",
        default=1,
        action="store"
    )
    parser.add_argument(
        "-seed",
        type=int,
        help="Seed for random number generator",
        action="store"
    )

    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()

    min_year, max_year, increment, year_list = common.build_year_list(args.y, args.p)

    # build list of keywords that we'll be making topic models for
    key_list = build_key_list(args.i)

    # add words in json file to stopwords set, if filepath is given
    if args.ignore is not None:
        stopwords = build_ignore_list(args.ignore, args.lang)
    else:
        stopwords = set(nltk.corpus.stopwords.words(args.lang))

    # add keywords in stopwords set if include_keys is not set
    if not args.include_keys:
        for key in key_list:
            sub_keys = key.split("_")
            for wd in sub_keys:
                stopwords.add(wd)

    doc_dict = init_sent_doc_dict(args.i, key_list, year_list, stopwords, min_year, max_year, text_type)
    dictionary_dict = build_frequency_dict(doc_dict, key_list, year_list)
    corpus_dict = common.build_dict_of_lists(year_list, key_list)

    if args.lsi:
        tfidf_dict = common.build_dict_of_lists(year_list, key_list)
        lsi_dict = common.build_dict_of_lists(year_list, key_list)
    else:
        lda_dict = common.build_dict_of_lists(year_list, key_list)
        if args.seed is not None:
            # generator seed
            rands = numpy.random.RandomState(args.seed)
    print("Building topic models.")
    for year in tqdm.tqdm(year_list):
        for key in key_list:
            corpus_dict[year][key] = \
                [dictionary_dict[year][key].doc2bow(doc) for doc in doc_dict[year][key]]
            numdocs = len(corpus_dict[year][key])
            if args.lsi:
                try:
                    tfidf_dict[year][key] = gensim.models.TfidfModel(corpus_dict[year][key])
                    tfidf = tfidf_dict[year][key]
                    lsi_dict[year][key] = gensim.models.LsiModel(
                        corpus=tfidf[corpus_dict[year][key]], id2word=dictionary_dict[year][key],
                        num_topics=200)
                except ValueError:
                    lsi_dict[year][key] = "No Documents for this period."
            else:
                try:
                    if args.seed is None:
                        # stochastic
                        lda_dict[year][key] = (gensim.models.ldamodel.LdaModel(
                            corpus=corpus_dict[year][key], id2word=dictionary_dict[year][key],
                            num_topics=args.num_topics, passes=args.passes), numdocs)
                    else:
                        # deterministic (ish)
                        lda_dict[year][key] = (gensim.models.ldamodel.LdaModel(
                            corpus=corpus_dict[year][key], id2word=dictionary_dict[year][key],
                            num_topics=args.num_topics, random_state=rands, passes=args.passes), numdocs)
                except ValueError:
                    lda_dict[year][key] = "No Documents for this period."

    with open(args.txt + '.txt', 'w', encoding='utf8') as txt_out:
        txt_out.write("Topics per period / keyword pair: " + "\n")
        for i in range(len(year_list) - 1):
            txt_out.write("Period: {0} - {1}".format(str(year_list[i]), str(year_list[i+1])) + "\n")
            for key in key_list:
                txt_out.write("For extracted documents around {0}:".format(str(key).replace("_", "/")) + "\n")
                txt_out.write("Number of documents for this period / keyword pair: {0}"
                              .format(str(lda_dict[year_list[i]][key][1])) + "\n")
                try:
                    if args.lsi:
                        try:
                            topics = lsi_dict[year_list[i]][key].show_topics(
                                num_topics=args.num_topics, num_words=args.num_words)
                        except TypeError:
                            topics = ["There were no documents for this period."]
                    else:
                        topics = lda_dict[year_list[i]][key][0].show_topics(
                            num_topics=args.num_topics, num_words=args.num_words)
                    j = 1
                    for topic in topics:
                        if args.weights:
                            topic = str(topic[1])
                            filtered = topic.split('+')
                            for k in range(len(filtered) - 1, -1, -1):
                                if filtered[k] == "" or filtered[k] == "None":
                                    del filtered[k]
                                else:
                                    filtered[k] = filtered[k].split('*')
                            for k in range(len(filtered)):
                                if k == 0:
                                    txt_out.write("Topic {0}: {1} ({2}), "
                                                  .format(str(j), filtered[k][1].strip(), filtered[k][0].strip()))
                                elif k == len(filtered) - 1:
                                    txt_out.write("{0} ({1})"
                                                  .format(filtered[k][1].strip(), filtered[k][0].strip()))
                                else:
                                    txt_out.write("{0} ({1}), "
                                                  .format(filtered[k][1].strip(), filtered[k][0].strip()))
                        else:
                            topic = str(topic)
                            filtered = re.split('\W[0-9]*', topic)
                            for k in range(len(filtered) - 1, -1, -1):
                                if filtered[k] == "" or filtered[k] == "None":
                                    del filtered[k]
                                else:
                                    filtered[k] = filtered[k].lower()
                            txt_out.write("Topic {0}: {1}".format(str(j), ", ".join(filtered)))
                        j += 1
                        txt_out.write("\n")
                    txt_out.write("\n")
                except AttributeError:
                    txt_out.write(lda_dict[year_list[i]][key])
            txt_out.write("\n")