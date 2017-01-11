import gensim, os, argparse, json, collections, re, nltk, numpy


# construct list of year periods, if user wants to model topics by year
def build_year_list(increment, range_years):
    if not periods:
        num_elements = int(((yrange_max - yrange_min) / increment))
        year_list = [None] * num_elements
        i = 0
        for num in range(yrange_min, yrange_max, increment):
            year_list[i] = num
            i += 1
    else:
        num_elements = len(range_years)
        year_list = [None] * num_elements
        i = 0
        for num in range_years:
            year_list[i] = int(num)
            i += 1
    return sorted(year_list)


# construct list of keywords
def build_key_list(keywords):
    key_list = keywords.lower().split(",")
    key_list = [keyword.strip() for keyword in key_list]
    key_list = set(key_list)
    return key_list


# build a nested dict with lists as values
def build_dict_of_lists(year_list):
    results = {}
    for year in year_list:
        results[year] = []
    return results


# build a nested dict with lists as values
def build_dict_of_dicts(year_list):
    results = {}
    for year in year_list:
            results[year] = {}
    return results


# declare / add to set of stopwords
def build_ignore_list(path_to_file):
    stopwords = set(nltk.corpus.stopwords.words(language))
    with open(path_to_file, 'r', encoding='utf-8') as ignored_list:
        jsondata = json.load(ignored_list)
        # check format of ignored file, old version has all ignored
        # words under a field called "Ignored". this check should be
        # removed in the future when everyone is using same ignore file
        try:
            ignored = jsondata["Ignored"]
            ignore_flag = True
        except KeyError:
            ignore_flag = False
        if ignore_flag:
            for ignore in ignored:
                stopwords.add(ignore)
        else:
            # load different categories, add tokens to stopwords set
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
    return stopwords


# determine which field of the json file to read from
def determine_text_type(type_arg):
    if type_arg.lower() == "full":
        text_field = "Full Sentences"
    elif type_arg.lower() == "filtered":
        text_field = "Filtered Sentences"
    elif type_arg.lower() == "stemmed":
        text_field = "Stemmed Sentences"
    elif type_arg.lower() == "filtered stemmed":
        text_field = "Filtered Stemmed Sentences"
    else:
        text_field = type_arg
    return text_field


# build dictionary of documents, separated by period. this dictionary is used in
# conjunction with the build_frequency_dict function to yield a dictionary of
# 'bag of words' representations of each individual document.
def init_sent_doc_dict(input_dir, year_list, stopwords):
    doc_dict = build_dict_of_lists(year_list)
    for dirs, subdirs, files in os.walk(input_dir):
        for jsondoc in files:
            if jsondoc[0] != ".":
                with open(input_dir + "/" + jsondoc, 'r', encoding='utf8') as inpt:
                    jsondata = json.load(inpt)
                    year = int(jsondata["Year Published"])
                    # check to make sure it's within range specified by user
                    if yrange_min <= year < yrange_max:
                        # determine which period it falls within
                        for i in range(len(year_list)):
                            if year_list[i] <= year < year_list[i + 1]:
                                target = year_list[i]
                                break
                            if year >= year_list[len(year_list) - 1]:
                                target = year_list[len(year_list) - 1]
                                break
                            else:
                                continue
                        # load sentences from jsondoc
                        text = jsondata[text_type]
                        for document in text:
                            doc_split = document.split()
                            # filter each sentence
                            for i in range(len(doc_split) - 1, -1, -1):
                                if doc_split[i] in stopwords or len(doc_split[i]) < 2:
                                    del doc_split[i]
                            try:
                                # add filtered sentence to document set
                                doc_dict[target].append(doc_split)
                            except KeyError:
                                pass
    return doc_dict


# yields word frequency for each document read in. used with init_sent_doc_dict
# to construct the 'bag of words' representation for each document.
def build_frequency_dict(doc_dict, year_list):
    dictionary = build_dict_of_dicts(year_list)
    for year in year_list:
        frequency = collections.defaultdict(int)
        for doc in doc_dict[year]:
            for token in doc:
                frequency[token] += 1
        texts = [[token for token in doc if frequency[token] > 1]
                 for doc in doc_dict[year]]
        dictionary[year] = gensim.corpora.Dictionary(texts)
    return dictionary


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", metavar='in-directory', action="store", help="input directory argument")
    parser.add_argument("-txt", help="output text file argument", action="store")
    parser.add_argument("-num_topics", action="store", help="number of topics to display")
    parser.add_argument("-num_words", action="store", help="number of words per topic")
    parser.add_argument("-weights", action="store_true", help="display topic weights with topics")
    parser.add_argument("-lang", action="store", help="language")
    parser.add_argument("-type", action="store", help="json field to analyze")
    parser.add_argument("-ignore", action="store", help="path to ignored list json file")
    parser.add_argument("-p", help="boolean to analyze by different periods rather than a fixed increment value",
                        action="store_true")
    parser.add_argument("-y", help="min/max for year range and increment value, surround with quotes",
                        action="store")
    parser.add_argument("-k", help="list of keywords argument, surround list with quotes", action="store")
    parser.add_argument("-passes", help="number of passes on corpus", action="store")
    parser.add_argument("-seed", help="generator seed for deterministic(ish) modeling", action="store")

    try:
        args = parser.parse_args()
    except IOError as msg:
        print(parser.error(str(msg)))

    def fail(msg):
        print(msg)
        os._exit(1)

    print("Initializing Variables.")

    # set up global values
    global yrange_min, yrange_max, periods, text_type, language

    if args.num_topics is None:
        num_topics = 10
    else:
        num_topics = int(args.num_topics)

    if args.num_words is None:
        num_words = 10
    else:
        num_words = int(args.num_words)

    if args.passes is None:
            passes = 1
    else:
        passes = int(args.passes)

    if args.k is not None:
        key_list = build_key_list(args.k)
        keys = True
    else:
        keys = False

    weights = args.weights
    periods = args.p
    language = args.lang

    text_type = determine_text_type(args.type)

    # if periods flag is not set, set up variables for fixed increments
    if not periods:
        range_years = args.y.split()
        yrange_min = int(range_years[0])
        increment = int(range_years[2])
        difference = int(range_years[1]) - yrange_min
        mod_val = difference % increment
        # adjust list of years so the end bit doesn't get cut out
        if mod_val != 0:
            yrange_max = int(range_years[1]) + (increment - mod_val) + increment
        else:
            yrange_max = int(range_years[1]) + increment
        # initialize list of years
        year_list = build_year_list(increment, range_years)
    # set up variables for periods rather than fixed increments
    else:
        range_years = args.y.split()
        yrange_min = int(range_years[0])
        yrange_max = int(range_years[len(range_years) - 1])
        increment = 0
        # initialize list of years
        year_list = build_year_list(increment, range_years)

    # build list of keywords that we'll be making topic models for
    key_list = build_key_list(args.i)

    print("Building Ignore List.")

    # add words in json file to stopwords set
    if args.ignore is not None:
        stopwords = build_ignore_list(args.ignore)
    else:
        stopwords = set(nltk.corpus.stopwords.words(language))

    print("Building Corpus Dictionary.")

    doc_dict = init_sent_doc_dict(args.i, year_list, stopwords)

    print("Building Frequency Dictionary.")

    dictionary_dict = build_frequency_dict(doc_dict, year_list)

    corpus_dict = build_dict_of_lists(year_list)

    lda_dict = build_dict_of_lists(year_list)

    print("Building LDA Models")
    for year in year_list:
        try:
            corpus_dict[year] = \
                [dictionary_dict[year].doc2bow(doc) for doc in doc_dict[year]]
            lda_dict[year] = gensim.models.ldamulticore.LdaMulticore(
                corpus=corpus_dict[year], id2word=dictionary_dict[year],
                num_topics=num_topics, passes=passes)
        except ValueError:
            lda_dict[year] = "No Documents for this period."

    with open(args.txt + '.txt', 'w', encoding='utf8') as txt_out:
        txt_out.write("Topics per period / keyword pair: " + "\n")
        for i in range(len(year_list) - 1):
            txt_out.write("Period: {0} - {1}".format(str(year_list[i]), str(year_list[i+1])) + "\n")
            try:
                topics = lda_dict[year_list[i]].show_topics(
                    num_topics=num_topics, num_words=num_words)
                j = 1
                for topic in topics:
                    if weights:
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
                        if keys:
                            for word in filtered:
                                if word in key_list:
                                    txt_out.write("Topic {0}: {1}".format(str(j), ", ".join(filtered)))
                                    break
                        else:
                            txt_out.write("Topic {0}: {1}".format(str(j), ", ".join(filtered)))
                    j += 1
                    txt_out.write("\n")
                txt_out.write("\n")
            except AttributeError:
                txt_out.write(lda_dict[year_list[i]])
        txt_out.write("\n")


if __name__ == '__main__':
    main()
