import json, math, os, nltk, argparse, csv


#                           *** WordFrequencyScript.py ***
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


# construct list of keywords
def buildKeyList(keywords):
    key_list = keywords.lower().split()
    return key_list


# construct list of year periods
def buildYearList(increment, range_years):
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


# simplest dict with numbers as values, used for calculating word percentage
def buildSimpleDictOfNums(year_list):
    results = {}
    for year in year_list:
        results[year] = 0
    return results


# simplest dict with lists as values, used for calculating the top n words
def buildSimpleDictOfLists(year_list):
    results = {}
    for year in year_list:
        results[year] = []
    return results


# build a nested dict with lists as values
def buildDictOfLists(year_list, keywords):
    results = {}
    for year in year_list:
        for keyword in keywords:
            try:
                results[year][keyword] = []
            except KeyError:
                results[year] = {keyword: []}
    return results


# build a nested dict with individual numbers as values
def buildDictOfNums(year_list, keywords):
    results = {}
    for year in year_list:
        for keyword in keywords:
            try:
                results[year][keyword] = 0
            except KeyError:
                results[year] = {keyword: 0}
    return results


# build dict used to keep track of how many books user has
# inputted for a given decade, used for calculating idf
def buildYearsTally(directory, year_list):
    years_tally = {}
    for y in year_list:
        try:
            years_tally[y] = 0
        except KeyError:
            pass
    for subdir, dirs, files in os.walk(directory):
        for jsondoc in files:
            if jsondoc[0] != ".":
                with open(directory + "/" + jsondoc, 'r', encoding='utf8') as in_file:
                    jsondata = json.load(in_file)
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
                            years_tally[target] += 1
                        except KeyError:
                            pass
    return years_tally


# calculates idf score for each keyword/decade pair
def calculateIDFResults(keywords, year_list, years_tally, directory):
    idf_results = buildDictOfNums(year_list, keywords)
    for subdir, dirs, files in os.walk(directory):
        for jsondoc in files:
            if jsondoc[0] != ".":
                with open(directory + "/" + jsondoc, 'r', encoding='utf8') as in_file:
                    jsondata = json.load(in_file)
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
                        # create word frequency distribution
                        fdist = nltk.FreqDist(text)
                        for keyword in keywords:
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
def calculateTF_IDFResults(year_list, keywords, directory, idf_results):
    tf_idf_results = buildDictOfLists(year_list, keywords)
    for subdir, dirs, files in os.walk(directory):
        for jsondoc in files:
            if jsondoc[0] != ".":
                with open(directory + "/" + jsondoc, 'r', encoding='utf8') as inpt:
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
                        # create word frequency distribution
                        fdist = nltk.FreqDist(text)
                        # calculate tf and tf-idf for each keyword
                        for keyword in keywords:
                            words = keyword.split("/")
                            temp = 0
                            for w in words:
                                temp += calculateTF(fdist, w)
                            try:
                                idf = idf_results[target][keyword]
                                tf_idf = calculateTF_IDF(idf, temp)
                                # append tuple of document/tf-idf score pair
                                tf_idf_results[target][keyword].append((jsondoc, tf_idf))
                            except KeyError:
                                pass
    for year in year_list:
        for keyword in keywords:
            tf_idf_results[year][keyword] = sorted(tf_idf_results[year][keyword], key=lambda x: x[1])
    return tf_idf_results


# calculate term frequency for tf-idf results
def calculateTF(fdist, w):
    termFreq = fdist[w]
    try:
        maxFreq = fdist[fdist.max()]
        tf = (termFreq / maxFreq)
    except ValueError:
        # Text empty, maxFreq = 0
        tf = 0
    return tf


# take product of tf and idf score
def calculateTF_IDF(idf_score, tf_score):
    tf_idf = tf_score * idf_score
    return tf_idf


# returns avg tf-idf score for each decade
def tf_idfAvg(year_list, keywords, tf_idf_results):
    tf_idf_avg = buildDictOfNums(year_list, keywords)
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


# returns maximum tf-idf score for each decade
def tf_idfMax(year_list, keywords, tf_idf_results):
    tf_idf_max = buildDictOfNums(year_list, keywords)
    # Take max of tf-idf results
    for i in range(len(year_list)):
        for keyword in keywords:
            try:
                length = len(tf_idf_results[year_list[i]][keyword])
                # the lists in tf_idf results are sorted by the second
                # tuple value, so max is second entry in the last tuple
                maximum = tf_idf_results[year_list[i]][keyword][length - 1][1]
                tf_idf_max[year_list[i]][keyword] = maximum
            except (ValueError, IndexError) as e:
                # no files for this period
                prev_year = year_list[i - 1]
                try:
                    prev_max = tf_idf_max[prev_year][keyword]
                except KeyError:
                    # case when the first period in the list of dates
                    # has no files associated with it.
                    prev_max = 0
                tf_idf_max[year_list[i]][keyword] = prev_max
    return tf_idf_max


# returns minimum tf-idf score for each decade
def tf_idfMin(year_list, keywords, tf_idf_results):
    tf_idf_min = buildDictOfNums(year_list, keywords)
    # Take max of tf-idf results
    for i in range(len(year_list)):
        for keyword in keywords:
            try:
                # the lists in tf_idfResults are sorted by the second
                # tuple value, so min is second entry in the first tuple
                minimum = tf_idf_results[year_list[i]][keyword][0][1]
                tf_idf_min[year_list[i]][keyword] = minimum
            except (ValueError, IndexError) as e:
                # no files for this period
                prev_year = year_list[i - 1]
                try:
                    prev_min = tf_idf_min[prev_year][keyword]
                except KeyError:
                    # case when the first period in the list of dates
                    # has no files associated with it.
                    prev_min = 0
                tf_idf_min[year_list[i]][keyword] = prev_min
    return tf_idf_min


# returns total word count for each decade
def totalWordCount(year_list, directory):
    word_totals = buildSimpleDictOfNums(year_list)
    for subdir, dirs, files in os.walk(directory):
        for jsondoc in files:
            if jsondoc[0] != ".":
                with open(directory + "/" + jsondoc, 'r', encoding='utf8') as in_file:
                    jsondata = json.load(in_file)
                    text = jsondata[text_type]
                    words = len(text)
                    year = int(jsondata["Year Published"])
                    # check to make sure it's within range specified by user
                    if yrange_min <= year < yrange_max:
                        for i in range(len(year_list)):
                            # determine which period it falls within
                            if year_list[i] <= year < year_list[i + 1]:
                                target = year_list[i]
                                break
                            if year >= year_list[len(year_list) - 1]:
                                target = year_list[len(year_list) - 1]
                                break
                            else:
                                continue
                        try:
                            word_totals[target] += words
                        except KeyError:
                            # year out of range specified by user
                            pass
    return word_totals


# returns total keyword count for each keyword/decade pair
def keywordCount(year_list, keywords, directory):
    keyword_totals = buildDictOfNums(year_list, keywords)
    for subdir, dirs, files in os.walk(directory):
        for jsondoc in files:
            if jsondoc[0] != ".":
                with open(directory + "/" + jsondoc, 'r', encoding='utf8') as in_file:
                    jsondata = json.load(in_file)
                    text = jsondata[text_type]
                    year = int(jsondata["Year Published"])
                    # check to make sure it's within range specified by user
                    if yrange_min <= year < yrange_max:
                        for i in range(len(year_list)):
                            # determine which period it falls within
                            if year_list[i] <= year < year_list[i + 1]:
                                target = year_list[i]
                                break
                            if year >= year_list[len(year_list) - 1]:
                                target = year_list[len(year_list) -1]
                                break
                            else:
                                continue
                        # create word frequency distribution
                        fdist = nltk.FreqDist(text)
                        for keyword in keywords:
                            # update keyword count for period/keyword pair
                            words = keyword.split("/")
                            for w in words:
                                word_count = fdist[w]
                                try:
                                    keyword_totals[target][keyword] += word_count
                                except KeyError:
                                    # decade out of range (specified by user)
                                    pass
    return keyword_totals


# calculates term frequency for each keyword/decade pair as a
# percentage of the total words in all books for each decade
def takeKeywordPercentage(year_list, keywords, total_words, keyword_totals):
    keyword_percentages = buildDictOfNums(year_list, keywords)
    for i in range(len(year_list)):
        for keyword in keywords:
            num = keyword_totals[year_list[i]][keyword]
            den = total_words[year_list[i]]
            if den > 0:
                percent = round((num / den) * 100, 4)
                keyword_percentages[year_list[i]][keyword] = percent
            else:
                # no files for this decade, use previous decade's totals
                prev_year = year_list[i - 1]
                try:
                    percent = keyword_percentages[prev_year][keyword]
                except KeyError:
                    # case when the first period in the list of dates
                    # has no files associated with it.
                    percent = 0
                keyword_percentages[year_list[i]][keyword] = percent
    return keyword_percentages


# first need a list of all the words for frequency distribution
def obtainWordList(directory, year_list, target):
    word_list = []
    for subdir, dirs, files in os.walk(directory):
        for jsondoc in files:
            if jsondoc[0] != ".":
                with open(directory + "/" + jsondoc, 'r', encoding='utf8') as in_file:
                    jsondata = json.load(in_file)
                    year = int(jsondata["Year Published"])
                    # check to make sure it's within range specified by user
                    if yrange_min <= year < yrange_max:
                        # determine which period it falls within
                        for i in range(len(year_list)):
                            if year_list[i] <= year < year_list[i + 1]:
                                t = year_list[i]
                                break
                            if year >= year_list[len(year_list) - 1]:
                                t = year_list[len(year_list) - 1]
                                break
                            else:
                                continue
                        # test if this document belongs to the range of years whose
                        # word list is being built
                        if t == target:
                            text = jsondata[text_type]
                            word_list.extend(text)
    return word_list


# might need a set of word_list (minimizes redundancy / faster lookup)
def wordListToSet(word_list):
    word_set = set()
    for word in word_list:
        word_set.add(word)
    return word_set


# build list of top words
def obtainNWords(fdist, num, total_words):
    keywords = []
    # list of top words / frequency tuples in frequency distribution (fdist)
    n_list = fdist.most_common(num)
    for key_tup in n_list:
        keywords.append((key_tup[0], round((key_tup[1] / total_words) * 100, 4)))
    return keywords


# build dict of top words along with their individual frequencies
def calculateNWords(year_list, directory, num):
    n_dict = buildSimpleDictOfLists(year_list)
    # build full word list for each period
    for year in year_list:
        word_list = obtainWordList(directory, year_list, year)
        total_words = len(word_list)
        fdist = nltk.FreqDist(word_list)
        if num <= len(fdist):
            # make sure user requested less top words than are actually
            # in the frequency distribution for that period
            n_dict[year].extend(obtainNWords(fdist, num, total_words))
        else:
            # user requested more top words than there are
            # in the frequency distribution for that period
            n_dict[year].extend(obtainNWords(fdist, len(fdist), total_words))
    return n_dict


# returns a list of values to be plotted
def buildGraphList(keyword, year_list, param):
    i = 0
    a = [0] * len(year_list)
    while i < len(year_list):
        a[i] += param[year_list[i]][keyword]
        i += 1
    return a


# writes N documents with highest tf-idf scores for each period to a text file
def listMaxDocs(out, year, keyword, results, num):
    list_length = len(results[year][keyword])
    if int(num) <= list_length:
        # make sure user requested less tf-idf scores than actually exist for that period
        out.write("{0} highest TF-IDF scores for \"{1}\" in this period: ".format(str(num), str(keyword)) + "\n")
        i = 1
        for key_tup in results[year][keyword][list_length - int(num): list_length]:
            out.write("{0}. {1}: {2}".format(str(i), str(key_tup[0]), str(key_tup[1])) + "\n")
            i += 1
    else:
        # user requested more tf-idf scores than there are for that period
        out.write("{0} highest TF-IDF scores for \"{1}\" in this period: ".format(str(list_length), str(keyword)) + "\n")
        i = 1
        for key_tup in results[year][keyword]:
            out.write("{0}. {1}: {2}".format(str(i), str(key_tup[0]), str(key_tup[1])) + "\n")
            i += 1


# writes N documents with lowest tf-idf scores for each period to a text file
def listMinDocs(out, year, keyword, results, num):
    list_length = len(results[year][keyword])
    if int(num) <= list_length:
        # make sure user requested less tf-idf scores than actually exist for that period
        out.write("{0} lowest TF-IDF scores for \"{1}\" in this period: ".format(str(num), str(keyword)) + "\n")
        i = 1
        for key_tup in results[year][keyword][:int(num)]:
            out.write("{0}. {1}: {2}".format(str(i), str(key_tup[0]), str(key_tup[1])) + "\n")
            i += 1
        out.write("\n")
    else:
        # user requested more tf-idf scores than there are for that period
        out.write("{0} lowest TF-IDF scores for \"{1}\" in this period: ".format(str(list_length), str(keyword)) + "\n")
        i = 1
        for key_tup in results[year][keyword]:
            out.write("{0}. {1}: {2}".format(str(i), str(key_tup[0]), str(key_tup[1])) + "\n")
            i += 1
        out.write("\n")


# writes N highest occurring words for each period to a text file
def listTopWords(out, year, results, num):
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


# can't store lists in csv file, so need to store data in string
def listToString(list_inpt):
    return_string = ""
    for wd in list_inpt:
        return_string += (str(wd) + " ")
    return return_string


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", metavar='in-directory', action="store", help="input directory argument")
    parser.add_argument("-txt", help="output text file argument", action="store")
    parser.add_argument("-csv", help="output csv file argument", action="store")
    parser.add_argument("-k", help="list of keywords argument, surround list with quotes", action="store")
    parser.add_argument("-y", help="min/max for year range and increment value, surround with quotes",
                        action="store")
    parser.add_argument("-num", help="number of words to grab from each decade, according to whichever metric "
                                     "is chosen to be graphed", action="store")
    parser.add_argument("-p", help="boolean to analyze by different periods rather than a fixed increment value",
                        action="store_true")
    parser.add_argument("-periods", help="list of periods, include cutoff date for last period as last entry",
                        action="store")
    parser.add_argument("-type", help="which text field from the json document you intend to analyze",
                        action="store")

    try:
        args = parser.parse_args()
    except IOError:
        pass

    # set up necessary values
    directory = args.i
    keywords = buildKeyList(args.k)

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

        # initialize list of years and dict to keep track of
        # how many books between each year range
        year_list = buildYearList(increment, range_years)
        years_tally = buildYearsTally(directory, year_list)

    # set up variables for periods rather than fixed increments
    else:
        range_years = args.periods.split()
        yrange_min = int(range_years[0])
        yrange_max = int(range_years[len(range_years) - 1])
        increment = 0

        # initialize list of years and dict to keep track of
        # how many books in each period
        year_list = buildYearList(increment, range_years)
        years_tally = buildYearsTally(directory, year_list)

    # build/populate dicts
    idf_results = calculateIDFResults(keywords, year_list, years_tally, directory)
    tf_idf_results = calculateTF_IDFResults(year_list, keywords, directory, idf_results)
    # take avg/max/min
    tf_idf_avg = tf_idfAvg(year_list, keywords, tf_idf_results)
    tf_idf_max = tf_idfMax(year_list, keywords, tf_idf_results)
    tf_idf_min = tf_idfMin(year_list, keywords, tf_idf_results)
    # take percent over total words for each keyword
    total_words = totalWordCount(year_list, directory)
    keyword_totals = keywordCount(year_list, keywords, directory)
    keyword_percentage = takeKeywordPercentage(year_list, keywords, total_words, keyword_totals)

    # calculate top N words for each period, check if user set -num first
    try:
        n_dict = calculateNWords(year_list, directory, int(args.num))
    except TypeError:
        pass

    # create txt file and write all the collected data to it
    with open(args.txt + '.txt', 'w') as txt_out:
        txt_out.write("Corresponding CSV file for this text document is located on your machine at the "
                      "following filepath: {0}".format(args.csv))
        for i in range(len(year_list) - 1):
            txt_out.write("Period: {0} - {1}".format(str(year_list[i]), str(year_list[i+1])) + "\n")
            txt_out.write("Number of books for this period: {0}".format(str(years_tally[year_list[i]])) + "\n")
            for keyword in keywords:
                txt_out.write("{0}:".format(str(keyword)) + "\n")
                txt_out.write("Avg TFIDF score for this period: {0}".format(str(tf_idf_avg[year_list[i]][keyword]) + "\n"))
                txt_out.write("Max TFIDF score for this period: {0}".format(str(tf_idf_max[year_list[i]][keyword]) + "\n"))
                txt_out.write("Min TFIDF score for this period: {0}".format(str(tf_idf_min[year_list[i]][keyword]) + "\n"))
                txt_out.write("Word frequency for \"{0}\" (as percentage of total words) for this period: {1}".format(
                    keyword, str(keyword_percentage[year_list[i]][keyword]) + "\n"))
                try:
                    listMaxDocs(txt_out, year_list[i], keyword, tf_idf_results, args.num)
                    listMinDocs(txt_out, year_list[i], keyword, tf_idf_results, args.num)
                except (AttributeError, UnboundLocalError, TypeError) as e:
                    # user didn't want max/min n words
                    pass
            try:
                listTopWords(txt_out, year_list[i], n_dict, args.num)
            except (AttributeError, UnboundLocalError) as e:
                # user didn't want top n words, so n_dict wasn't built
                pass
            txt_out.write("\n")

    with open(args.csv + '.csv', 'w', newline='') as csv_out:
        csvwriter = csv.writer(csv_out, delimiter=',')
        year_list_str = []
        for year in year_list:
            year_list_str.append(str(year))
        year_string = " ".join(year_list_str)
        csvwriter.writerow(['word', 'tf-idf avg', 'tf-idf max', 'tf-idf min', 'word frequency', year_string])
        for keyword in keywords:
            csvwriter.writerow([keyword, listToString(buildGraphList(keyword, year_list, tf_idf_avg)),
                                 listToString(buildGraphList(keyword, year_list, tf_idf_max)),
                                 listToString(buildGraphList(keyword, year_list, tf_idf_min)),
                                 listToString(buildGraphList(keyword, year_list, keyword_percentage))])

if __name__ == '__main__':
    main()
