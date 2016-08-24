import json
import os
import nltk
import argparse
import math
import matplotlib.pyplot as plt
import numpy as np


#                           *** WordFrequencyScript.py ***
# Takes Json documents organized in a specific way and performs various statistics on them w/r/t
# keywords provided by the user. As of 8/13/16 this script supports avg/max/min calculations for tfidf
# scoring as well as basic term frequency as a percentage of total words. Any one of these four metrics
# can be represented on a graph, and all four of them are provided in a text file at the end of each run.
#


# construct list of keywords
def buildKeyList(keywords):
    keyList = keywords.split()
    return keyList


# construct list of decades
# should I have range_years as global or passed to the function?
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
def buildSimpleDictOfNums(decades):
    results = {}
    for decade in decades:
        results[decade] = 0
    return results


# simplest dict with lists as values, used for calculating the top n words
def buildSimpleDictOfLists(decades):
    results = {}
    for decade in decades:
        results[decade] = []
    return results


# build a dict with lists as values
def buildDictOfLists(decades, keywords):
    results = {}
    for decade in decades:
        for keyword in keywords:
            try:
                results[decade][keyword] = []
            except KeyError:
                results[decade] = {keyword: []}
    return results


# build a dict with individual numbers as values
def buildDictOfNums(decades, keywords):
    results = {}
    for decade in decades:
        for keyword in keywords:
            try:
                results[decade][keyword] = 0
            except KeyError:
                results[decade] = {keyword: 0}
    return results


# build dict used to keep track of how many books
# the user has inputted for a given decade
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
                    year = int(jsondata["4.Year Published"])
                    # check to make sure it's within range specified by user
                    if yrange_min <= year < yrange_max:
                        for i in range(len(year_list)):
                            # check if doing fixed increments or periods
                            if not periods:
                                if year_list[i] <= year < year_list[i + 1] or year == year_list[i + 1]:
                                    target = year_list[i]
                                    break
                                else:
                                    i += 1
                            else:
                                if year_list[i] <= year < year_list[i + 1]:
                                    target = year_list[i]
                                    break
                                else:
                                    i += 1
                        try:
                            years_tally[target] += 1
                        except KeyError:
                            pass
    return years_tally


# take product of tf and idf score
def calculateTF_IDF(idfScore, tfScore):
    tf_idf = tfScore * idfScore
    return tf_idf


# returns avg tfidf score for each decade
def tf_idfAvg(decades, keywords, tf_idfResults):
    tf_idf_avg = buildDictOfNums(decades, keywords)
    # Take avg of TFIDF results
    for i in range(len(decades)):
        for keyword in keywords:
            length = len(tf_idfResults[decades[i]][keyword])
            total = sum(tf_idfResults[decades[i]][keyword])
            # check if there exist files for the period
            if length > 0 or total > 0:
                try:
                    avg = round((total / length), 4)
                    tf_idf_avg[decades[i]][keyword] = avg
                except ZeroDivisionError:
                    tf_idf_avg[decades[i]][keyword] = 0
            else:
                # no files, use previous period's score
                prev_decade = decades[i - 1]
                try:
                    prev_avg = tf_idf_avg[prev_decade][keyword]
                except KeyError:
                    # case when the first period in the list of dates
                    # has no files associated with it.
                    prev_avg = 0
                tf_idf_avg[decades[i]][keyword] = prev_avg
    return tf_idf_avg


# returns maximum tfidf score for each decade
def tf_idfMax(decades, keywords, tf_idfResults):
    tf_idf_max = buildDictOfNums(decades, keywords)
    # Take max of TFIDF results
    for i in range(len(decades)):
        for keyword in keywords:
            try:
                maximum = max(tf_idfResults[decades[i]][keyword])
                tf_idf_max[decades[i]][keyword] = maximum
            except ValueError:
                # no files for this period
                prev_decade = decades[i - 1]
                try:
                    prev_max = tf_idf_max[prev_decade][keyword]
                except KeyError:
                    # case when the first period in the list of dates
                    # has no files associated with it.
                    prev_max = 0
                tf_idf_max[decades[i]][keyword] = prev_max
    return tf_idf_max


# returns minimum tfidf score for each decade
def tf_idfMin(decades, keywords, tf_idfResults):
    tf_idf_min = buildDictOfNums(decades, keywords)
    # Take max of TFIDF results
    for i in range(len(decades)):
        for keyword in keywords:
            try:
                minimum = min(tf_idfResults[decades[i]][keyword])
                tf_idf_min[decades[i]][keyword] = minimum
            except ValueError:
                # no files for this period
                prev_decade = decades[i - 1]
                try:
                    prev_min = tf_idf_min[prev_decade][keyword]
                except KeyError:
                    # case when the first period in the list of dates
                    # has no files associated with it.
                    prev_min = 0
                tf_idf_min[decades[i]][keyword] = prev_min
    return tf_idf_min


# calculate term frequency for tfidf
def calculateTF(fdist, w):
    termFreq = fdist[w]
    try:
        maxFreq = fdist[fdist.max()]
        TF = (termFreq / maxFreq)
    except ValueError:
        # Text empty, maxFreq = 0
        TF = 0
    return TF


# calculates term frequency for each keyword/decade pair, then multiplies it
# with the idf score for that decade, yielding a tfidf score for each keyword/document pair.
# The results are stored in a dict, and ordered by decade.
def calculateTF_IDFResults(decades, keywords, directory, idf_results):
    tf_idf_results = buildDictOfLists(decades, keywords)
    for subdir, dirs, files in os.walk(directory):
        for jsondoc in files:
            if jsondoc[0] != ".":
                with open(directory + "/" + jsondoc, 'r', encoding='utf8') as inpt:
                    jsondata = json.load(inpt)
                    text = jsondata["9.Filtered Text"]
                    year = int(jsondata["4.Year Published"])
                    # check to make sure it's within range specified by user
                    if yrange_min <= year < yrange_max:
                        for i in range(len(decades)):
                            if decades[i] <= year < decades[i + 1] or year == decades[i + 1]:
                                decade = decades[i]
                                break
                            else:
                                i += 1
                         # create word frequency distribution
                        fdist = nltk.FreqDist(text)
                        for keyword in keywords:
                            words = keyword.split("/")
                            temp = 0
                            for w in words:
                                temp += calculateTF(fdist, w)
                            try:
                                idf = idf_results[decade][keyword]
                                tf_idf = calculateTF_IDF(idf, temp)
                                tf_idf_results[decade][keyword].append(tf_idf)
                            except KeyError:
                                pass
    return tf_idf_results


# calculates idf score for each keyword/decade pair
def calculateIDFResults(keywords, year_list, years_tally, directory):
    idf_results = buildDictOfNums(year_list, keywords)
    for subdir, dirs, files in os.walk(directory):
        for jsondoc in files:
            if jsondoc[0] != ".":
                with open(directory + "/" + jsondoc, 'r', encoding='utf8') as in_file:
                    jsondata = json.load(in_file)
                    text = jsondata["9.Filtered Text"]
                    year = int(jsondata["4.Year Published"])
                    # check to make sure it's within range specified by user
                    if yrange_min <= year < yrange_max:
                        for i in range(len(year_list)):
                            # check if doing fixed increments or periods
                            if not periods:
                                if year_list[i] <= year < year_list[i + 1] or year == year_list[i + 1]:
                                    target = year_list[i]
                                    break
                                else:
                                    i += 1
                            else:
                                if year_list[i] <= year < year_list[i + 1]:
                                    target = year_list[i]
                                    break
                                else:
                                    i += 1
                        # create word frequency distribution
                        fdist = nltk.FreqDist(text)
                        for keyword in keywords:
                            words = keyword.split("/")
                            for w in words:
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
                # Add 1 before logarithm to ensure idf is nonzero
                idf_results[y][keyword] = \
                    1 + round(math.log((years_tally[y]) / idf_results[y][keyword], 10), 4) \
                        if idf_results[y][keyword] > 0 else 0
            except KeyError:
                pass
    return idf_results


# returns total word count for each decade
def totalWordCount(year_list, directory):
    word_totals = buildSimpleDictOfNums(year_list)
    for subdir, dirs, files in os.walk(directory):
        for jsondoc in files:
            if jsondoc[0] != ".":
                with open(directory + "/" + jsondoc, 'r', encoding='utf8') as in_file:
                    jsondata = json.load(in_file)
                    text = jsondata["9.Filtered Text"]
                    words = len(text)
                    year = int(jsondata["4.Year Published"])
                    # check to make sure it's within range specified by user
                    if yrange_min <= year < yrange_max:
                        for i in range(len(year_list)):
                            # check if doing fixed increments or periods
                            if not periods:
                                if year_list[i] <= year < year_list[i + 1] or year == year_list[i + 1]:
                                    target = year_list[i]
                                    break
                                else:
                                    i += 1
                            else:
                                if year_list[i] <= year < year_list[i + 1]:
                                    target = year_list[i]
                                    break
                                else:
                                    i += 1
                        try:
                            word_totals[target] += words
                        except KeyError:
                            # decade out of range (specified by user)
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
                    text = jsondata["9.Filtered Text"]
                    year = int(jsondata["4.Year Published"])
                    # check to make sure it's within range specified by user
                    if yrange_min <= year < yrange_max:
                        for i in range(len(year_list)):
                            # check if doing fixed increments or periods
                            if not periods:
                                if year_list[i] <= year < year_list[i + 1] or year == year_list[i + 1]:
                                    target = year_list[i]
                                    break
                                else:
                                    i += 1
                            else:
                                if year_list[i] <= year < year_list[i + 1]:
                                    target = year_list[i]
                                    break
                                else:
                                    i += 1
                        # create word frequency distribution
                        fdist = nltk.FreqDist(text)
                        for keyword in keywords:
                            words = keyword.split("/")
                            for w in words:
                                word_count = fdist[w]
                                try:
                                    keyword_totals[target][keyword] += word_count
                                except KeyError:
                                    # decade out of range (specified by user)
                                    pass
    return keyword_totals


# calculates term frequency for each keyword/decade pair as a percentage
# of the total words in all books for each decade
# NEED TO FIX, so as not to rely on "increment", fucks with the previous decade shit for
# the end of period based analysis. probably need to fix it in the other tf-idf methods
# too
def takeKeywordPercentage(decades, keywords, total_words, keyword_totals):
    keyword_percentages = buildDictOfNums(decades, keywords)
    for i in range(len(decades)):
        for keyword in keywords:
            num = keyword_totals[decades[i]][keyword]
            den = total_words[decades[i]]
            if den > 0:
                percent = round((num / den) * 100, 4)
                keyword_percentages[decades[i]][keyword] = percent
            else:
                # no files for this decade, use previous decade's totals
                prev_decade = decades[i - 1]
                try:
                    percent = keyword_percentages[prev_decade][keyword]
                except KeyError:
                    # case when the first period in the list of dates
                    # has no files associated with it.
                    percent = 0
                keyword_percentages[decades[i]][keyword] = percent
    return keyword_percentages


# returns a list of values to be plotted
def buildGraphList(keyword, decades, param):
    i = 0
    a = [0] * len(decades)
    while i < len(decades):
        a[i] += param[decades[i]][keyword]
        i += 1
    return a


# first need a list of all the words for frequency distribution
def obtainWordList(directory, year_list, target):
    word_list = []
    for subdir, dirs, files in os.walk(directory):
        for jsondoc in files:
            if jsondoc[0] != ".":
                with open(directory + "/" + jsondoc, 'r', encoding='utf8') as in_file:
                    jsondata = json.load(in_file)
                    year = int(jsondata["4.Year Published"])
                    # check to make sure it's within range specified by user
                    if yrange_min <= year < yrange_max:
                        for i in range(len(year_list)):
                            # check if doing fixed increments or periods

                            # fixed increments
                            if not periods:
                                if year_list[i] <= year < year_list[i + 1] or year == year_list[i + 1]:
                                    t = year_list[i]
                                    break
                                else:
                                    i += 1

                            # periods
                            else:
                                if year_list[i] <= year < year_list[i + 1]:
                                    t = year_list[i]
                                    break
                                else:
                                    i += 1

                        # test if this document belongs to the range of years whose
                        # word list is being built
                        if t == target:
                            text = jsondata["9.Filtered Text"]
                            word_list.extend(text)
    return word_list


# might need a set of word_list (minimizes redundancy / faster lookup)
def wordListToSet(word_list):
    word_set = set()
    for word in word_list:
        word_set.add(word)
    return word_set


# build list of words
def obtainNWords(fdist, num, total_words):
    keywords = []
    n_list = fdist.most_common(num)
    for key_tup in n_list:
        keywords.append((key_tup[0], round((key_tup[1] / total_words) * 100, 4)))
    return keywords


def calculateNWords(decades, directory, num):
    n_dict = buildSimpleDictOfLists(decades)
    for decade in decades:
        word_list = obtainWordList(directory, decades, decade)
        total_words = len(word_list)
        fdist = nltk.FreqDist(word_list)
        n_dict[decade].extend(obtainNWords(fdist, num, total_words))
    return n_dict


# find max value used in graphed results
def findMax(keywords, decades, results):
    g_max = 0
    for decade in decades:
        for keyword in keywords:
            if results[decade][keyword] > g_max:
                g_max = results[decade][keyword]
    return g_max


# find min value used in graphed results
def findMin(keywords, decades, results, g_max):
    g_min = g_max
    for decade in decades:
        for keyword in keywords:
            if results[decade][keyword] < g_max:
                g_min = results[decade][keyword]
    return g_min


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", metavar='in-directory', action="store", help="input directory argument")
    parser.add_argument("-o", help="output file argument", action="store")
    parser.add_argument("-k", help="list of keywords argument, surround list with quotes", action="store")
    parser.add_argument("-y", help="min/max for year range and increment value, surround with quotes",
                        action="store")
    parser.add_argument("-t_avg", help="take tf_idf avg for each decade", action="store_true")
    parser.add_argument("-t_max", help="take tf_idf max for each decade", action="store_true")
    parser.add_argument("-t_min", help="take tf_idf min for each decade", action="store_true")
    parser.add_argument("-percent", help="graph word frequency as a percentage of total words (not tfidf)",
                        action="store_true")
    parser.add_argument("-num", help="number of words to grab from each decade, according to whichever metric "
                                     "is chosen to be graphed", action="store")
    parser.add_argument("-bar", help="plot data as a bar graph (default is line)", action="store_true")
    parser.add_argument("-p", help="boolean to graph by different periods rather than a fixed increment value",
                        action="store_true")
    parser.add_argument("-periods", help="list of periods, include cutoff date for last period as last entry",
                        action="store")

    try:
        args = parser.parse_args()
    except IOError:
        pass

    def fail(msg):
        print(msg)
        os._exit(1)

    # set up necessary values
    directory = args.i
    keywords = buildKeyList(args.k)

    global yrange_min, yrange_max, periods

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

    # check to make sure only one of the avg/max/min flags are set
    check = []
    check.append(int(args.t_avg)), check.append(int(args.t_max)), \
    check.append(int(args.t_min)), check.append(int(args.percent))
    if sum(check) > 1:
        fail("Please enter a maximum of one of the following arguments: -avg, -max, -min, -percent")

    if args.t_avg or args.t_max or args.t_min or args.percent:
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

    # calculate top N words for each decade, but check if user set -num first
    try:
        n = int(args.num)
        n_dict = calculateNWords(year_list, directory, n)
    except TypeError:
        pass

    # create txt file and write all the collected data to it
    out = open(args.o + ".txt", 'w')
    for decade in year_list:
        out.write("Decade: " + str(decade) + "\n")
        out.write("Number of books for this decade: " + str(years_tally[decade]) + "\n")
        if args.t_avg or args.t_max or args.t_min or args.percent:
            for keyword in keywords:
                out.write(keyword + ":" + "\n")
                out.write("Avg TFIDF score for this decade: {0}".format(str(tf_idf_avg[decade][keyword]) + "\n"))
                out.write("Max TFIDF score for this decade: {0}".format(str(tf_idf_max[decade][keyword]) + "\n"))
                out.write("Min TFIDF score for this decade: {0}".format(str(tf_idf_min[decade][keyword]) + "\n"))
                out.write("Word frequency (as percentage of total words) for this decade: {0}".format(
                    str(keyword_percentage[decade][keyword]) + "%\n"))
        try:
            out.write("Top {0} words for this decade: ".format(str(args.num)) + "\n")
            i = 1
            for key_tup in n_dict[decade]:
                out.write(str(i) + ". " + str(key_tup[0]) + ": " + str(key_tup[1]) + "%\n")
                i += 1
            out.write("\n")
        except (AttributeError, UnboundLocalError) as e:
            # user didn't want top n words, so n_dict wasn't built
            pass
        out.write("\n")

    if args.bar:
        if not periods:
            bar_width = increment / len(keywords)
            index = np.arange(int(range_years[0]), int(range_years[1]) + int(range_years[2]), int(range_years[2]))
        else:
            range = yrange_max - yrange_min
            bar_width = (range / (len(range_years) - 1)) / len(keywords)
            range_years_int = []
            for num in range_years:
                range_years_int.append(int(num))
            index = np.array(sorted(range_years_int))
        opacity = .8

        i = 0
        for keyword in keywords:
            if args.percent:
                plt.bar(index + (bar_width * i), buildGraphList(keyword, year_list, keyword_percentage),
                        bar_width, alpha=opacity, color=np.random.rand(3, 1), label=keyword)
            if args.t_avg:
                plt.bar(index + (bar_width * i), buildGraphList(keyword, year_list, tf_idf_avg),
                        bar_width, alpha=opacity, color=np.random.rand(3, 1), label=keyword)
            if args.t_max:
                plt.bar(index + (bar_width * i), buildGraphList(keyword, year_list, tf_idf_max),
                        bar_width, alpha=opacity, color=np.random.rand(3, 1), label=keyword)
            if args.t_min:
                plt.bar(index + (bar_width * i), buildGraphList(keyword, year_list, tf_idf_min),
                        bar_width, alpha=opacity, color=np.random.rand(3, 1), label=keyword)
            i += 1

        if args.t_avg or args.t_max or args.t_min or args.percent:
            plt.xlabel("Decade")
            plt.ylabel("Word Frequency")
            if args.t_avg:
                plt.title("TF-IDF Average Scores Per Decade")
            if args.t_max:
                plt.title("TF-IDF Maximum Scores Per Decade")
            if args.t_min:
                plt.title("TF-IDF Minimum Scores Per Decade")
            if args.percent:
                plt.title("Word Frequency as Percentage of Total Words Per Decade")
            plt.xticks(index + 5, (year for year in year_list))
            plt.legend()
            plt.show()
    else:

        # determine graph parameters, depending on which flag is set
        if args.t_avg:
            g_max = findMax(keywords, year_list, tf_idf_avg)
            g_min = findMin(keywords, year_list, tf_idf_avg, g_max)
        if args.t_max:
            g_max = findMax(keywords, year_list, tf_idf_max)
            g_min = findMin(keywords, year_list, tf_idf_max, g_max)
        if args.t_min:
            g_max = findMax(keywords, year_list, tf_idf_min)
            g_min = findMin(keywords, year_list, tf_idf_min, g_max)
        if args.percent:
            g_max = findMax(keywords, year_list, keyword_percentage)
            g_min = findMin(keywords, year_list, keyword_percentage, g_max)

        # plot data according to which of the four flags are set
        for keyword in keywords:
            if args.t_avg:
                plt.plot(year_list, buildGraphList(keyword, year_list, tf_idf_avg), label=keyword)
            if args.t_max:
                plt.plot(year_list, buildGraphList(keyword, year_list, tf_idf_max), label=keyword)
            if args.t_min:
                plt.plot(year_list, buildGraphList(keyword, year_list, tf_idf_min), label=keyword)
            if args.percent:
                plt.plot(year_list, buildGraphList(keyword, year_list, keyword_percentage), label=keyword)

        # specifies graph params/labels
        if args.t_avg or args.t_max or args.t_min or args.percent:
            if args.t_avg:
                plt.title("TF-IDF Average Scores Per Decade")
            if args.t_max:
                plt.title("TF-IDF Maximum Scores Per Decade")
            if args.t_min:
                plt.title("TF-IDF Minimum Scores Per Decade")
            if args.percent:
                plt.title("Word Frequency as Percentage of Total Words Per Decade")
            plt.legend(bbox_to_anchor=(1, .1, 0, .1), ncol=int(len(keywords)/2),
                       mode="expand", borderaxespad=0.)
            plt.xlabel("Decade")
            plt.ylabel("Word Frequency")
            if (g_min - .05) < 0:
                plt.axis([yrange_min, yrange_max - increment, 0, g_max + .05])
            else:
                plt.axis([yrange_min, yrange_max - increment, g_min - .05, g_max + .05])
            plt.show()

if __name__ == '__main__':
    main()
