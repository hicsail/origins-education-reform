import gensim, os, argparse, json, collections, re
import logging


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


# build list of keywords
def build_key_list(directory):
    key_list = []
    for dirs, subdirs, files in os.walk(directory):
        for subdir in subdirs:
            key_list.append(subdir)
    return key_list


# build a nested dict with lists as values
def build_dict_of_lists(year_list, key_list):
    results = {}
    for year in year_list:
        for key in key_list:
            try:
                results[year][key] = []
            except KeyError:
                results[year] = {key: []}
    return results


# build a nested dict with lists as values
def build_dict_of_dicts(year_list, key_list):
    results = {}
    for year in year_list:
        for key in key_list:
            try:
                results[year][key] = {}
            except KeyError:
                results[year] = {key: {}}
    return results


# separate year / keyword pairs into lists of texts. this dictionary is used in
# conjunction with the build_frequency_dict function to yield a dictionary of
# 'bag of words' representations of each individual document.
def init_sent_doc_dict(input_dir, key_list, year_list):
    doc_dict = build_dict_of_lists(year_list, key_list)
    for dirs, subdirs, files in os.walk(input_dir):
        # 'subdir' corresponds to each keyword
        for subdir in subdirs:
            for folders, subfolders, file in os.walk(dirs + "/" + subdir):
                for jsondoc in file:
                    if jsondoc[0] != ".":
                        with open(dirs + "/" + subdir + "/" + jsondoc, 'r', encoding='utf8') as inpt:
                            jsondata = json.load(inpt)
                            text = jsondata[text_type]
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
                                try:
                                    doc_dict[target][subdir].append(text)
                                except KeyError:
                                    pass
    return doc_dict


# yields word frequency for each document read in. used with init_sent_doc_dict
# to construct the 'bag of words' representation for each document.
def build_frequency_dict(doc_dict, key_list, year_list):
    dictionary = build_dict_of_dicts(year_list, key_list)
    for year in year_list:
        for key in key_list:
            frequency = collections.defaultdict(int)
            for doc in doc_dict[year][key]:
                for token in doc:
                    frequency[token] += 1
            texts = [[token for token in doc if frequency[token] > 1]
                     for doc in doc_dict[year][key]]
            dictionary[year][key] = gensim.corpora.Dictionary(texts)
    return dictionary


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", metavar='in-directory', action="store", help="input directory argument")
    parser.add_argument("-txt", help="output text file argument", action="store")
    parser.add_argument("-type", action="store", help="name of text field in json doc")
    parser.add_argument("-num_topics", action="store", help="number of topics to display")
    parser.add_argument("-num_words", action="store", help="number of words per topic")
    parser.add_argument("-p", help="boolean to analyze by different periods rather than a fixed increment value",
                        action="store_true")
    parser.add_argument("-y", help="min/max for year range and increment value, surround with quotes",
                        action="store")

    try:
        args = parser.parse_args()
    except IOError:
        pass

    # logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

    # build separate doc lists for each subdir, compute topic models on each doc list

    # set up global values
    global yrange_min, yrange_max, periods, text_type

    text_type = args.type
    periods = args.p

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
        range_years = args.periods.split()
        yrange_min = int(range_years[0])
        yrange_max = int(range_years[len(range_years) - 1])
        increment = 0

        # initialize list of years
        year_list = build_year_list(increment, range_years)

    # build list of keywords that we'll be making topic models for
    key_list = build_key_list(args.i)

    # doc_dict = build_dict_of_dicts(year_list, key_list)

    doc_dict = init_sent_doc_dict(args.i, key_list, year_list)
    dictionary_dict = build_frequency_dict(doc_dict, key_list, year_list)

    corpus_dict = build_dict_of_lists(year_list, key_list)
    lda_dict = build_dict_of_lists(year_list, key_list)
    for year in year_list:
        for key in key_list:
            corpus_dict[year][key] = [dictionary_dict[year][key].doc2bow(doc) for doc in doc_dict[year][key]]
            # gensim.corpora.MmCorpus.serialize('/tmp/{0}{1}.mm'.format(year, key), corpus_dict[year][key])
            # corpus_dict[year][key] = gensim.corpora.MmCorpus('/tmp/{0}{1}.mm'.format(year, key))
            try:
                lda_dict[year][key] = gensim.models.LdaModel(
                    corpus_dict[year][key], id2word=dictionary_dict[year][key], num_topics=int(args.num_topics))
            except ValueError:
                lda_dict[year][key] = "No Documents for this period."

    with open(args.txt + '.txt', 'w') as txt_out:
        txt_out.write("Topics per period / keyword pair: " + "\n")
        for i in range(len(year_list) - 1):
            txt_out.write("Period: {0} - {1}".format(str(year_list[i]), str(year_list[i+1])) + "\n")
            for key in key_list:
                txt_out.write("For extracted documents around {0}:".format(str(key)) + "\n")
                try:
                    topics = lda_dict[year_list[i]][key].show_topics(
                        num_topics=int(args.num_topics), num_words=int(args.num_words))
                    j = 1
                    for topic in topics:
                        topic = str(topic)
                        filtered = re.split('\W[0-9]*', topic)
                        for i in range(len(filtered) - 1, -1, -1):
                            if filtered[i] == "" or filtered[i] == "None":
                                del filtered[i]
                            else:
                                filtered[i] = filtered[i].lower()
                        txt_out.write("Topic {0}: {1}".format(str(j), ", ".join(filtered)))
                        j += 1
                        txt_out.write("\n")
                    txt_out.write("\n")
                except AttributeError:
                    txt_out.write(lda_dict[year_list[i]][key])
            txt_out.write("\n")


if __name__ == '__main__':
    main()
