import math, os, nltk, argparse, json, tqdm
from statistics import mean, variance
import common


#                           *** WordFrequency.py ***
#
# Takes Json documents as input and performs various statistics on them w/r/t keywords provided
# by the user. As of 9/1/16 this script supports avg/max/min calculations for tf-idf scoring as
# well as basic term frequency as a percentage of total words. All four of these metrics are provided
# in a text file at the end of each run. The text file can also include an arbitrary number (specified
# by the user) of max/min tf-idf scores along with their respective documents, as well as a list of
# words with top frequencies per period.
#
# Update 9/28: Input argument -b will allow the user to analyze bigrams rather than individual keywords.
# All other script functionality is the same.
#

def determine_year(year):
    if year < yrange_min:
        return -1
    if year >= yrange_max:
        return -1

    index = (year - yrange_min) // increment
    start_year = index * increment + yrange_min
    return start_year

# calculate term frequency for tf-idf results
def calculate_tf(freq_dist, w):
    termFreq = freq_dist[w]
    maxFreq = freq_dist[freq_dist.max()]

    tf = 0
    if maxFreq > 0:
        tf = termFreq / maxFreq

    return tf

def build_nested_dict_of_nums(year_list, keywords):
    results = {}
    for year in year_list:
        results[year] = {}
        for keyword in keywords:
            results[year][keyword] = {}
            for k in keyword.split("/"):
                results[year][keyword][k] = 0
    return results

# simplest dict with lists as entries
def build_simple_dict_of_lists(year_list):
    results = {}
    for year in year_list:
        results[year] = []
    return results

# PER DOCUMENT FUNCTIONS

def process_documents(keywords, periods, directory, num):
    years_tally = {start_year: 0 for start_year in periods}
    tf_results = common.build_dict_of_lists(periods, keywords)
    idf_results = common.build_dict_of_nums(periods, keywords)
    document_tally = common.build_dict_of_nums(periods, keywords)
    tfidf_results = common.build_dict_of_lists(periods, keywords)
    word_totals = common.build_simple_dict_of_nums(periods)
    word_count_dict = build_nested_dict_of_nums(periods, keywords)
    frequency_list = common.build_dict_of_lists(periods, keywords)
    freq_dist_dict = {start_year: None for start_year in periods}
    text_lengths = common.build_simple_dict_of_nums(periods)
    n_dict = build_simple_dict_of_lists(periods)

    for _, _, files in os.walk(directory):
        print("Processing documents:")
        for jsondoc in tqdm.tqdm(files):
            if jsondoc[0] == ".":
                continue
            with open(directory + "/" + jsondoc, 'r', encoding='utf8') as in_file:
                jsondata = json.load(in_file)
                text = jsondata[field]
                length = len(text)
                if bigrams:
                    text = nltk.bigrams(text)
                    length = len(text)
                freq_dist = nltk.FreqDist(text)

                year = int(jsondata["Year"])
                if year < yrange_min:
                    continue
                if year >= yrange_max:
                    continue
                start_year = determine_year(year)

                tally_documents_in_year(start_year, years_tally)
                tally_keywords_in_document(freq_dist, start_year, keywords, document_tally)
                compute_word_counts(freq_dist, start_year, keywords, word_totals, word_count_dict, frequency_list, length)
                compute_document_tf(freq_dist, start_year, keywords, tf_results)
                if num is not None:
                    compute_document_n_words(freq_dist, length, start_year, freq_dist_dict, text_lengths, n_dict)

    # Reduce
    for start_year in periods:
        # Compute top words
        obtain_n_words(freq_dist_dict[start_year], num, text_lengths[start_year], start_year, n_dict)

        for keyword in keywords:
            # Compute IDF
            idf = 0
            if document_tally[start_year][keyword] > 0:
                assert(years_tally[start_year] >= document_tally[start_year][keyword])
                idf = 1 + math.log((years_tally[start_year]) / document_tally[start_year][keyword], 10)
            idf_results[start_year][keyword] = idf

            # Compute TF-IDFs
            tfidfs = [tf * idf for tf in tf_results[start_year][keyword]]
            tfidf_results[start_year][keyword] = tfidfs

    return years_tally, idf_results, tfidf_results, word_count_dict, frequency_list, word_totals, n_dict

# Adds 1 to the tally if a document is in a given period
def tally_documents_in_year(start_year, years_tally):
    years_tally[start_year] += 1

# Adds 1 to the tally if a keyword appears in the given document
def tally_keywords_in_document(freq_dist, start_year, keywords, document_tally):
    for keyword in keywords:
        if not bigrams:
            words = keyword.split("/")
            for w in words:
                if freq_dist[w] > 0:
                    document_tally[start_year][keyword] += 1
                    break
        else:
            for keyphrase in keyword:
                if freq_dist[keyphrase] > 0:
                    document_tally[start_year][keyphrase] += 1
                    break

# Computes the TF value for keywords in the document
def compute_document_tf(freq_dist, start_year, keywords, tf_results):
    for keyword in keywords:
        tf = 0
        if not bigrams:
            words = keyword.split("/")
            for w in words:
                tf += calculate_tf(freq_dist, w)
        else:
            for i in range(len(keyword)):
                tf += calculate_tf(freq_dist, keyword[i])

        tf_results[start_year][keyword].append(tf)

def compute_word_counts(freq_dist, start_year, keyword_sets, word_totals, word_count_dict, frequency_list, length):
    for keyword_set in keyword_sets:
        # keeping this here for bigrams
        word_count = 0
        # update keyword count for period/keyword pair
        if not bigrams:
            keyword_set_split = keyword_set.split("/")
            for keyword in keyword_set_split:
                word_count += freq_dist[keyword]
                word_count_dict[start_year][keyword_set][keyword] += freq_dist[keyword]
        else:
            for keyphrase in keyword_sets:
                if keyphrase in freq_dist:
                    word_count += freq_dist[keyphrase]
        
        word_totals[start_year] += length
        frequency_list[start_year][keyword_set].append(word_count)

# build list of top words
def obtain_n_words(freq_dist, num, total_words, year, n_dict):
    if freq_dist is None:
        return

    keywords = []
    n_list = freq_dist.most_common(num)
    for key_tup in n_list:
        keywords.append((key_tup[0], (key_tup[1] / total_words) * 100))
    n_dict[year].extend(keywords)

def compute_document_n_words(freq_dist, text_len, start_year, freq_dist_dict, text_lengths, n_dict):
    text_lengths[start_year] += text_len
    if freq_dist_dict[start_year] is None:
        freq_dist_dict[start_year] = freq_dist
    else:
        freq_dist_dict[start_year] += freq_dist

# FULL CORPUS FUNCTIONS

def calculate_tfidf_stats(periods, keywords, tfidf_results):
    tf_idf_avg = common.build_dict_of_nums(periods, keywords)
    tf_idf_min = common.build_dict_of_nums(periods, keywords)
    tf_idf_max = common.build_dict_of_nums(periods, keywords)
    print("Calculating TF-IDF statistics")
    for i in tqdm.tqdm(range(len(periods))):
        period = periods[i]

        for keyword in keywords:
            # If there are no documents in the year period, use the previous
            # period's maximums and minimums to maintain continuity
            if tfidf_results[period][keyword] != []:
                tf_idf_avg[period][keyword] = mean(tfidf_results[period][keyword])
                tf_idf_min[period][keyword] = min(tfidf_results[period][keyword])
                tf_idf_max[period][keyword] = max(tfidf_results[period][keyword])
            elif i > 0:
                tf_idf_avg[period][keyword] = tf_idf_avg[periods[i-1]][keyword]
                tf_idf_min[period][keyword] = tf_idf_min[periods[i-1]][keyword]
                tf_idf_max[period][keyword] = tf_idf_max[periods[i-1]][keyword]
            else:
                tf_idf_avg[period][keyword] = 0
                tf_idf_min[period][keyword] = 0
                tf_idf_max[period][keyword] = 0

    return tf_idf_avg, tf_idf_min, tf_idf_max

# calculates term frequency for each keyword/decade pair as a
# percentage of the total words in all books for each decade
def take_keyword_percentage(periods, keywords, total_words, keyword_totals):
    keyword_percentages = build_nested_dict_of_nums(periods, keywords)
    print("Calculating per-word word frequency statistics")
    for i in tqdm.tqdm(range(len(periods))):
        period = periods[i]
        den = total_words[period]

        for keyword in keywords:
            for k in keyword.split("/"):
                if den > 0:
                    keyword_percentages[period][keyword][k] = keyword_totals[period][keyword][k] / den * 100
                elif i > 0:
                    keyword_percentages[period][keyword][k] = keyword_percentages[periods[i-1]][keyword][k]
                else:
                    keyword_percentages[period][keyword][k] = 0

    return keyword_percentages

# take average keyword occurrence across all volumes, using dict that stores list of individual frequencies
def calculate_frequency_stats(periods, keywords, frequency_lists):
    averages = common.build_dict_of_nums(periods, keywords)
    variances = common.build_dict_of_nums(periods, keywords)
    
    print("Calculating per-document word frequency statistics")
    for year in tqdm.tqdm(periods):
        for keyword in keywords:
            if len(frequency_lists[year][keyword]) > 1:
                averages[year][keyword] = mean(frequency_lists[year][keyword])
                variances[year][keyword] = variance(frequency_lists[year][keyword], \
                    averages[year][keyword])
            elif len(frequency_lists[year][keyword]) == 1:
                averages[year][keyword] = mean(frequency_lists[year][keyword])
                variances[year][keyword] = 0
            else:
                averages[year][keyword] = 0
                variances[year][keyword] = 0
    
    return averages, variances

# OUTPUT FUNCTIONS

# writes N highest occurring words for each period to a text file
def output_top_words(out, year, results, num):
    num = min(num, len(results[year]))
    out.write("Top {0} words for this period: ".format(len(results[year])) + "\n")
    for i in range(num):
        out.write("{0}. {1}: {2}".format(i, results[year][i][0], results[year][i][1]) + "\n")
    out.write("\n")

def build_json(in_dict):
    jfile = json.dumps(in_dict, sort_keys=False, indent=4, separators=(',', ': '), ensure_ascii=False)
    return jfile

def build_graph_list_from_nested(keyword, year_list, param, k):
    a = [0] * len(year_list)
    for i in range(len(year_list)):
        a[i] += param[year_list[i]][keyword][k]
    return a

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i",
        action="store",
        help="Input directory path",
        required=True
    )
    parser.add_argument(
        "-y",
        help="Start year, end year, and year increment for grouping texts",
        action="store",
        required=True
    )
    parser.add_argument(
        "-type",
        help="Selects the text field to use in analysis",
        default="Words",
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
        "-json",
        help="JSON output filename",
        action="store",
        required=True
    )
    parser.add_argument(
        "-k",
        help="List of words used for analysis",
        action="store",
        required=True
    )
    parser.add_argument(
        "-bigram",
        help="Set to analyze texts using bigrams rather than words",
        action="store_true"
    )
    parser.add_argument(
        "-num",
        type=int,
        help="Number of words to analyze from each decade",
        action="store"
    )
    parser.add_argument(
        "-label",
        action="store",
        help="Label associated with this corpus"
    )

    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()

    # set up global values
    global field, bigrams
    field = args.type
    bigrams = args.bigram

    # set up necessary values
    directory = args.i
    keywords = common.build_key_list(args.k, bigrams)

    # Handle year argument
    global yrange_min, yrange_max, increment
    [yrange_min, yrange_max, increment] = map(int, args.y.split())
    if yrange_max < yrange_min:
        raise Exception("Maximum year must be larger than minimum year.")
    if (yrange_max - yrange_min) % increment != 0:
        raise Exception("Increment does not evenly divide year range.")
    periods = list(range(yrange_min, yrange_max, increment))

    num_docs, idf_results, tfidf_results, word_count_dict, frequency_list, word_totals, n_dict \
        = process_documents(keywords, periods, directory, args.num)
    tf_idf_avg, tf_idf_min, tf_idf_max \
        = calculate_tfidf_stats(periods, keywords, tfidf_results)
    keyword_percentage = take_keyword_percentage(periods, keywords, word_totals, word_count_dict)
    keyword_averages, keyword_variances = calculate_frequency_stats(periods, keywords, frequency_list)

    out_periods = periods + [yrange_max]

    # create txt file and write all the collected data to it
    with open(args.txt + '.txt', 'w') as txt_out:
        txt_out.write("Corresponding Json file for this text document is located on your machine at the "
                      "following filepath: {0}".format(args.json) + "\n")
        print("Writing results to text file")
        for i in tqdm.tqdm(range(len(out_periods) - 1)):
            txt_out.write("Period: {0}-{1}".format(out_periods[i], out_periods[i+1]) + "\n")
            txt_out.write("Number of volumes for this period: {0}".format(str(num_docs[periods[i]])) + "\n")
            for keyword in keywords:
                txt_out.write("{0}:".format(str(keyword)) + "\n")
                txt_out.write("Average frequency of {0} for this period: {1}"
                              .format(keyword, str(keyword_averages[periods[i]][keyword]) + "\n"))
                txt_out.write("Variance for {0}: {1}"
                              .format(keyword, str(keyword_variances[periods[i]][keyword]) + "\n"))
                txt_out.write("Avg TF-IDF score for this period: {0}"
                              .format(str(tf_idf_avg[periods[i]][keyword]) + "\n"))
                txt_out.write("Max TF-IDF score for this period: {0}"
                              .format(str(tf_idf_max[periods[i]][keyword]) + "\n"))
                txt_out.write("Min TF-IDF score for this period: {0}"
                              .format(str(tf_idf_min[periods[i]][keyword]) + "\n"))
                txt_out.write("Word frequency for \"{0}\" (as percentage of total words) for this period: {1}"
                              .format(keyword, str(sum(keyword_percentage[periods[i]][keyword].values())) + "\n"))
                if args.num != None:
                    common.list_max_docs(txt_out, periods[i], keyword, tfidf_results, args.num, "TF-IDF")
                    common.list_min_docs(txt_out, periods[i], keyword, tfidf_results, args.num, "TF-IDF")
            if args.num != None:
                output_top_words(txt_out, periods[i], n_dict, args.num)
            txt_out.write("\n")

    jf = {}
    jf['label'] = args.label
    jf['year list'] = out_periods
    jf['number of documents'] = [num_docs[x] for x in num_docs]
    jf['keywords'] = keywords
    jf['breakdown'] = {}
    for keyword in keywords:
        jf[keyword] = {}
        jf[keyword]['tf-idf avg'] = common.build_graph_list(keyword, periods, tf_idf_avg)
        jf[keyword]['tf-idf max'] = common.build_graph_list(keyword, periods, tf_idf_max)
        jf[keyword]['tf-idf min'] = common.build_graph_list(keyword, periods, tf_idf_min)
        jf[keyword]['word frequency'] = [sum(keyword_percentage[year][keyword].values()) for year in keyword_percentage]
        jf[keyword]['average frequency'] = common.build_graph_list(keyword, periods, keyword_averages)
        jf[keyword]['variance'] = common.build_graph_list(keyword, periods, keyword_variances)
        for k in keyword.split('/'):
            jf['breakdown'][k] = build_graph_list_from_nested(keyword, periods, keyword_percentage, k)

    with open(args.json + '.json', 'w', encoding='utf-8') as jfile:
        jfile.write(build_json(jf))