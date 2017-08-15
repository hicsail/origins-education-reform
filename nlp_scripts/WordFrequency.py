import math, os, nltk, argparse, json, tqdm
import common


#                           *** WordFrequency.py ***
#
# Takes Json documents as input and performs various statistics on them w/r/t keywords provided
# by the user. As of 9/1/16 this script supports avg/max/min calculations for tf-idf scoring as
# well as basic term frequency as a percentage of total words. All four of these metrics are provided
# in a text file at the end of each run. The text file can also include an arbitrary number (specified
# by the user) of max/min tf-idf scores along with their respective documents, as well as a list of
# words with top frequencies per period. This script also outputs a csv file with tf-idf average, maximum,
# minimum and term frequency for each keyword specified. The statistics in this csv file can be read and
# graphed by another script called GraphCSV.py.
#
# Update 9/28: Input argument -b will allow the user to analyze bigrams rather than individual keywords.
# All other script functionality is the same.
#


# build dict used to keep track of how many books user has
# inputted for a given decade, used for calculating idf
def build_years_tally(directory, year_list, yrange_min, yrange_max):
    years_tally = {}
    for y in year_list:
        try:
            years_tally[y] = 0
        except KeyError:
            pass
    for subdir, dirs, files in os.walk(directory):
        print("Counting number of volumes per period.")
        for jsondoc in tqdm.tqdm(files):
            if jsondoc[0] != ".":
                with open(directory + "/" + jsondoc, 'r', encoding='utf-8') as in_file:
                    jsondata = json.load(in_file)
                    year = int(jsondata["Year Published"])
                    # check to make sure it's within range specified by user
                    if yrange_min <= year < yrange_max:
                        target = common.determine_year(year, year_list)
                        try:
                            years_tally[target] += 1
                        except KeyError:
                            pass
    return years_tally


# calculates idf score for each keyword/decade pair
def calculate_idf_results(keywords, year_list, years_tally, directory, yrange_min, yrange_max):
    idf_results = common.build_dict_of_nums(year_list, keywords)
    for subdir, dirs, files in os.walk(directory):
        print("Calculating IDF scores.")
        for jsondoc in tqdm.tqdm(files):
            if jsondoc[0] != ".":
                with open(directory + "/" + jsondoc, 'r', encoding='utf8') as in_file:
                    jsondata = json.load(in_file)
                    text = jsondata[text_type]
                    if bigrams:
                        text = nltk.bigrams(text)
                    year = int(jsondata["Year Published"])
                    # check to make sure it's within range specified by user
                    if yrange_min <= year < yrange_max:
                        target = common.determine_year(year, year_list)
                        # create word frequency distribution
                        fdist = nltk.FreqDist(text)
                        for keyword in keywords:
                            if not bigrams:
                                words = keyword.split("/")
                                for w in words:
                                    # check if word occurs in document
                                    if fdist[w] > 0:
                                        try:
                                            idf_results[target][keyword] += 1
                                            break
                                        except KeyError:
                                            pass
                                    else:
                                        pass
                            else:
                                for i in range(len(keyword)):
                                    if fdist[keyword[i]] > 0:
                                        try:
                                            idf_results[target][keyword] += 1
                                            break
                                        except KeyError:
                                            pass
                                    else:
                                        pass
    for y in year_list:
        for keyword in keywords:
            try:
                # Add 1 before logarithm to ensure idf is nonzero, unless the word doesn't
                # occur at all for the period, in which case it's idf score is 0.
                if idf_results[y][keyword] > 0:
                    idf_results[y][keyword] = 1 + round(math.log((years_tally[y]) / idf_results[y][keyword], 10), 4)
                else:
                    idf_results[y][keyword] = 0
            except KeyError:
                pass
    return idf_results


# calculates term frequency for each keyword/decade pair, then multiplies it with the idf score for that
# decade, yielding a tf-idf score for each keyword/document pair. The results are stored in a dict of tuples.
def calculate_tfidf_results(year_list, keywords, directory, idf_results, yrange_min, yrange_max):
    tf_idf_results = common.build_dict_of_lists(year_list, keywords)
    for subdir, dirs, files in os.walk(directory):
        print("Calculating TF-IDF scores.")
        for jsondoc in tqdm.tqdm(files):
            if jsondoc[0] != ".":
                with open(directory + "/" + jsondoc, 'r', encoding='utf8') as inpt:
                    jsondata = json.load(inpt)
                    text = jsondata[text_type]
                    if bigrams:
                        text = nltk.bigrams(text)
                    year = int(jsondata["Year Published"])
                    # check to make sure it's within range specified by user
                    if yrange_min <= year < yrange_max:
                        target = common.determine_year(year, year_list)
                        # create word frequency distribution
                        fdist = nltk.FreqDist(text)
                        # calculate tf and tf-idf for each keyword
                        for keyword in keywords:
                            # if single-word keywords are being searched for, then
                            # they can be grouped together, separated by a "/" character.
                            temp = 0
                            if not bigrams:
                                words = keyword.split("/")
                                for w in words:
                                    temp += calculate_tf(fdist, w)
                            else:
                                for i in range(len(keyword)):
                                    temp += calculate_tf(fdist, keyword[i])
                            try:
                                idf = idf_results[target][keyword]
                                tf_idf = calculate_tfidf(idf, temp)
                                # append tuple of document/tf-idf score pair
                                tf_idf_results[target][keyword].append((jsondoc, tf_idf))
                            except KeyError:
                                pass
    for year in year_list:
        for keyword in keywords:
            tf_idf_results[year][keyword] = sorted(tf_idf_results[year][keyword], key=lambda x: x[1])
    return tf_idf_results


# calculate term frequency for tf-idf results
def calculate_tf(fdist, w):
    termFreq = fdist[w]
    try:
        maxFreq = fdist[fdist.max()]
        tf = (termFreq / maxFreq)
    except ValueError:
        # Text empty, maxFreq = 0
        tf = 0
    return tf


# take product of tf and idf score
def calculate_tfidf(idf_score, tf_score):
    tf_idf = tf_score * idf_score
    return tf_idf


# returns avg tf-idf score for each decade
def calculate_tfidf_avg(year_list, keywords, tf_idf_results):
    tf_idf_avg = common.build_dict_of_nums(year_list, keywords)
    # take avg of tf-idf results
    for i in range(len(year_list)):
        for keyword in keywords:
            length = len(tf_idf_results[year_list[i]][keyword])
            totals = []
            for j in range(length):
                totals.append(tf_idf_results[year_list[i]][keyword][j][1])
            total = sum(totals)
            # check if there exist files for the period
            if length > 0 or total > 0:
                try:
                    avg = round((total / length), 4)
                    tf_idf_avg[year_list[i]][keyword] = avg
                except ZeroDivisionError:
                    tf_idf_avg[year_list[i]][keyword] = 0
            else:
                # no files, use previous period's score
                prev_year = year_list[i - 1]
                try:
                    prev_avg = tf_idf_avg[prev_year][keyword]
                except KeyError:
                    # case when the first period in the list of
                    # dates has no files associated with it.
                    prev_avg = 0
                tf_idf_avg[year_list[i]][keyword] = prev_avg
    return tf_idf_avg


# returns minimum tf-idf score for each decade
def calculate_tfidf_min_and_max(year_list, keywords, tf_idf_results):
    tf_idf_min = common.build_dict_of_nums(year_list, keywords)
    tf_idf_max = common.build_dict_of_nums(year_list, keywords)
    print("Calculating TF-IDF minimums & maximums")
    for i in tqdm.tqdm(range(len(year_list))):
        for keyword in keywords:
            try:
                length = len(tf_idf_results[year_list[i]][keyword])
                # the lists in tf_idfResults are sorted by the second
                # tuple value, so min is second entry in the first tuple
                minimum = tf_idf_results[year_list[i]][keyword][0][1]
                # likewise, max is second entry in the last tuple
                maximum = tf_idf_results[year_list[i]][keyword][length - 1][1]
                tf_idf_min[year_list[i]][keyword] = minimum
                tf_idf_max[year_list[i]][keyword] = maximum
            except (ValueError, IndexError) as e:
                # no files for this period
                try:
                    prev_min = tf_idf_min[year_list[i-1]][keyword]
                    prev_max = tf_idf_max[year_list[i-1]][keyword]
                except KeyError:
                    # case when the first period in the list of dates
                    # has no files associated with it.
                    prev_min, prev_max = 0
                tf_idf_min[year_list[i]][keyword] = prev_min
                tf_idf_max[year_list[i]][keyword] = prev_max
    return [tf_idf_min, tf_idf_max]


# returns total word count for each keyword/year period
def keyword_and_word_count(year_list, directory, yrange_min, yrange_max, keywords):
    word_totals = common.build_simple_dict_of_nums(year_list)
    word_count_dict = common.build_nested_dict_of_nums(year_list, keywords)
    # keyword_totals = common.build_dict_of_nums(year_list, keywords)
    frequency_list = common.build_dict_of_lists(year_list, keywords)
    # word_count = {}
    for subdir, dirs, files in os.walk(directory):
        print("Taking word counts")
        for jsondoc in tqdm.tqdm(files):
            if jsondoc[0] != ".":
                with open(directory + "/" + jsondoc, 'r', encoding='utf8') as in_file:
                    jsondata = json.load(in_file)
                    text = jsondata[text_type]
                    if bigrams:
                        text = nltk.bigrams(text)
                    num_words = len(list(text))
                    year = int(jsondata["Year Published"])
                    # check to make sure it's within range specified by user
                    if yrange_min <= year < yrange_max:
                        target = common.determine_year(year, year_list)
                        fdist = nltk.FreqDist(text)
                        for keyword in keywords:
                            # keeping this here for bigrams
                            word_count = 0
                            # update keyword count for period/keyword pair
                            if not bigrams:
                                keys = keyword.split("/")
                                for k in keys:
                                    word_count += fdist[k]
                                    word_count_dict[target][keyword][k] += fdist[k]
                            else:
                                # TODO: implement same functionality above for bigrams
                                # TODO: pretty much everything for bigrams is not functional
                                for i in range(len(keyword)):
                                    word_count += fdist[keyword[i]]
                            try:
                                # add word count to frequency totals (for frequency as percentage of total words)
                                # keyword_totals[target][keyword] += word_count
                                # append word count to frequency list (for mean & variance of samples)
                                # frequency_list[target][keyword].append(word_count)
                                word_totals[target] += num_words
                                word_count_dict[target][keyword]["TOTAL"] += word_count
                                frequency_list[target][keyword].append(word_count)
                            except KeyError:
                                # decade out of range
                                pass

    return [word_count_dict, frequency_list, word_totals]


# calculates term frequency for each keyword/decade pair as a
# percentage of the total words in all books for each decade
def take_keyword_percentage(year_list, keywords, total_words, keyword_totals):
    keyword_percentages = common.build_nested_dict_of_nums(year_list, keywords)
    print("Calculating keyword frequencies as percentages of total words")
    for i in tqdm.tqdm(range(len(year_list))):
        for keyword in keywords:
            num = keyword_totals[year_list[i]][keyword]["TOTAL"]
            den = total_words[year_list[i]]
            if den > 0:
                percent = round((num / den) * 100, 4)
                keyword_percentages[year_list[i]][keyword]["TOTAL"] = percent
            else:
                # no files for this decade, use previous decade's totals
                prev_year = year_list[i - 1]
                try:
                    percent = keyword_percentages[prev_year][keyword]["TOTAL"]
                except KeyError:
                    # case when the first period in the list of dates
                    # has no files associated with it.
                    percent = 0
                keyword_percentages[year_list[i]][keyword]["TOTAL"] = percent
            for k in keyword.split("/"):
                num = keyword_totals[year_list[i]][keyword][k]
                if den > 0:
                    percent = round((num / den) * 100, 4)
                    keyword_percentages[year_list[i]][keyword][k] = percent
                else:
                    prev_year = year_list[i - 1]
                    try:
                        percent = keyword_percentages[prev_year][keyword][k]
                    except KeyError:
                        percent = 0
                    keyword_percentages[year_list[i]][keyword][k] = percent
    return keyword_percentages


# take average keyword occurrence across all volumes, using dict that stores list of individual frequencies
def avg_and_var(year_list, keywords, frequency_lists):
    averages = common.build_dict_of_nums(year_list, keywords)
    variances = common.build_dict_of_nums(year_list, keywords)
    for year in year_list:
        for keyword in keywords:
            if len(frequency_lists[year][keyword]) > 0:
                averages[year][keyword] = \
                    sum(frequency_lists[year][keyword]) / len(frequency_lists[year][keyword])
                var = []
                for freq in frequency_lists[year][keyword]:
                    variance = math.pow((freq - averages[year][keyword]), 2)
                    var.append(variance)
                variances[year][keyword] = sum(var) / len(var)
            else:
                averages[year][keyword] = 0
                variances[year][keyword] = 0
    return [averages, variances]


# might need a set of word_list (minimizes redundancy / faster lookup)
def word_list_to_set(word_list):
    word_set = set()
    for word in word_list:
        word_set.add(word)
    return word_set


# build list of top words
def obtain_n_words(fdist, num, total_words):
    keywords = []
    # list of top words / frequency tuples in frequency distribution (fdist)
    n_list = fdist.most_common(num)
    for key_tup in n_list:
        keywords.append((key_tup[0], round((key_tup[1] / total_words) * 100, 4)))
    return keywords


def calculate_n_words(year_list, directory, num, yrange_min, yrange_max):
    fdist_dict = common.build_simple_dict_of_nums(year_list)
    text_lengths = common.build_simple_dict_of_nums(year_list)
    n_dict = common.build_simple_dict_of_lists(year_list)
    print("Calculating top {0} words per period".format(str(num)))
    for subdir, dirs, files in os.walk(directory):
        for jsondoc in files:
            if jsondoc[0] != ".":
                with open(directory + "/" + jsondoc, 'r', encoding='utf8') as in_file:
                    jsondata = json.load(in_file)
                    year = int(jsondata["Year Published"])
                    text = jsondata[text_type]
                    text_len = len(text)
                    if bigrams:
                        text = nltk.bigrams(text)
                        text_len = len(text)
                    fdist = nltk.FreqDist(text)
                    if yrange_min <= year < yrange_max:
                        target = common.determine_year(year, year_list)
                        text_lengths[target] += text_len
                        if fdist_dict[target] == 0:
                            fdist_dict[target] = fdist
                        else:
                            fdist_dict[target] |= fdist
    for year in year_list:
        if num <= len(fdist_dict[year]):
            n_dict[year].extend(obtain_n_words(fdist_dict[year], num, text_lengths[year]))
        else:
            n_dict[year].extend(obtain_n_words(fdist_dict[year], len(fdist_dict[year]), text_lengths[year]))
    return n_dict


# writes N highest occurring words for each period to a text file
def list_top_words(out, year, results, num):
    if int(num) <= len(results[year]):
        # make sure user requested less top words than actually exist for that period
        out.write("Top {0} words for this period: ".format(str(num)) + "\n")
        i = 1
        for key_tup in results[year]:
            out.write("{0}. {1}: {2}".format(str(i), str(key_tup[0]), str(key_tup[1])) + "\n")
            i += 1
    else:
        # user requested more top words than there are for that period
        out.write("Top {0} words for this period: ".format(str(len(results[year]))) + "\n")
        i = 1
        for key_tup in results[year]:
            out.write("{0}. {1}: {2}".format(str(i), str(key_tup[0], str(key_tup[1]))) + "\n")
    out.write("\n")


def build_json(in_dict):
    jfile = json.dumps(in_dict, sort_keys=False, indent=4, separators=(',', ': '), ensure_ascii=False)
    return jfile


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", metavar='in-directory', action="store", help="input directory argument")
    parser.add_argument("-txt", help="output text file argument", action="store")
    parser.add_argument("-json", help="output csv file argument", action="store")
    parser.add_argument("-b", help="boolean to control searching for bigrams rather than individual words",
                        action="store_true")
    parser.add_argument("-k", help="list of keywords argument, surround list with quotes", action="store")
    parser.add_argument("-y", help="min/max for year range and increment value, surround with quotes",
                        action="store")
    parser.add_argument("-num", help="number of words to grab from each decade, according to whichever metric "
                                     "is chosen to be graphed", action="store")
    parser.add_argument("-p", help="boolean to analyze by different periods rather than a fixed increment value",
                        action="store_true")
    parser.add_argument("-type", help="which text field from the json document you intend to analyze",
                        action="store")

    try:
        args = parser.parse_args()
    except IOError:
        pass

    # set up global values
    global text_type, bigrams

    if args.type is not None:
        text_type = args.type
    else:
        text_type = 'Words'
        
    periods = args.p
    bigrams = args.b

    # set up necessary values
    directory = args.i
    keywords = common.build_key_list(args.k, bigrams)

    range_years = args.y.split()
    year_params = common.year_params(range_years, periods)
    increment, yrange_min, yrange_max = year_params[0], year_params[1], year_params[2]

    # initialize list of years and dict to keep track
    # of how many books are within each year range
    year_list = common.build_year_list(increment, range_years, periods, yrange_max, yrange_min)
    years_tally = build_years_tally(directory, year_list, yrange_min, yrange_max)

    num_docs = []
    for year in year_list:
        num_docs.append(years_tally[year])

    # build/populate dicts
    idf_results = calculate_idf_results(keywords, year_list, years_tally, directory, yrange_min, yrange_max)
    tf_idf_results = calculate_tfidf_results(year_list, keywords, directory, idf_results, yrange_min, yrange_max)
    # take avg/max/min
    tf_idf_avg = calculate_tfidf_avg(year_list, keywords, tf_idf_results)
    min_and_max = calculate_tfidf_min_and_max(year_list, keywords, tf_idf_results)
    tf_idf_min = min_and_max[0]
    tf_idf_max = min_and_max[1]

    # returns word_count_dict and word_totals
    # counts[0] = keyword_totals
    # counts[1] = frequency_list
    # counts[2] = word_totals
    counts = keyword_and_word_count(year_list, directory, yrange_min, yrange_max, keywords)
    keyword_percentage = take_keyword_percentage(year_list, keywords, counts[2], counts[0])

    avg_var = avg_and_var(year_list, keywords, counts[1])
    keyword_averages = avg_var[0]
    keyword_variances = avg_var[1]

    # calculate top N words for each period, check if user set -num first
    try:
        n_dict = calculate_n_words(year_list, directory, int(args.num), yrange_min, yrange_max)
    except TypeError:
        pass

    # create txt file and write all the collected data to it
    with open(args.txt + '.txt', 'w') as txt_out:
        txt_out.write("Corresponding Json file for this text document is located on your machine at the "
                      "following filepath: {0}".format(args.json) + "\n")
        print("Writing results to text file")
        for i in tqdm.tqdm(range(len(year_list) - 1)):
            txt_out.write("Period: {0} - {1}".format(str(year_list[i]), str(year_list[i+1])) + "\n")
            txt_out.write("Number of volumes for this period: {0}".format(str(years_tally[year_list[i]])) + "\n")
            for keyword in keywords:
                txt_out.write("{0}:".format(str(keyword)) + "\n")
                txt_out.write("Average frequency of {0} for this period: {1}"
                              .format(keyword, str(keyword_averages[year_list[i]][keyword])) + "\n")
                txt_out.write("Variance for {0}: {1}"
                              .format(keyword, str(keyword_variances[year_list[i]][keyword])) + "\n")
                txt_out.write("Avg TF-IDF score for this period: {0}"
                              .format(str(tf_idf_avg[year_list[i]][keyword]) + "\n"))
                txt_out.write("Max TF-IDF score for this period: {0}"
                              .format(str(tf_idf_max[year_list[i]][keyword]) + "\n"))
                txt_out.write("Min TF-IDF score for this period: {0}"
                              .format(str(tf_idf_min[year_list[i]][keyword]) + "\n"))
                txt_out.write("Word frequency for \"{0}\" (as percentage of total words) for this period: {1}"
                              .format(keyword, str(keyword_percentage[year_list[i]][keyword]["TOTAL"]) + "\n"))
                try:
                    common.list_max_docs(txt_out, year_list[i], keyword, tf_idf_results, args.num, "TF-IDF")
                    common.list_min_docs(txt_out, year_list[i], keyword, tf_idf_results, args.num, "TF-IDF")
                except (AttributeError, UnboundLocalError, TypeError) as e:
                    # user didn't want max/min n words
                    pass
            try:
                list_top_words(txt_out, year_list[i], n_dict, args.num)
            except (AttributeError, UnboundLocalError) as e:
                # user didn't want top n words, so n_dict wasn't built
                pass
            txt_out.write("\n")

    jf = {}
    jf['year list'] = year_list
    jf['number of documents'] = num_docs
    jf['keywords'] = keywords
    jf['breakdown'] = {}
    for keyword in keywords:
        jf[keyword] = {}
        jf[keyword]['tf-idf avg'] = common.build_graph_list(keyword, year_list, tf_idf_avg)
        jf[keyword]['tf-idf max'] = common.build_graph_list(keyword, year_list, tf_idf_max)
        jf[keyword]['tf-idf min'] = common.build_graph_list(keyword, year_list, tf_idf_min)
        jf[keyword]['word frequency'] = common.build_graph_list_from_nested(
            keyword, year_list, keyword_percentage, 'TOTAL')
        jf[keyword]['average frequency'] = common.build_graph_list(keyword, year_list, keyword_averages)
        jf[keyword]['variance'] = common.build_graph_list(keyword, year_list, keyword_variances)
        for k in keyword.split('/'):
            jf['breakdown'][k] = common.build_graph_list_from_nested(keyword, year_list, keyword_percentage, k)

    with open(args.json + '.json', 'w', encoding='utf-8') as jfile:
        jfile.write(build_json(jf))

if __name__ == '__main__':
    main()
