import json
import os
import nltk
import argparse
import math
import matplotlib.pyplot as plt


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
def buildDecadesList(dmin, dmax, inc_val):
    decades_min = int(dmin)
    decades_max = int(dmax) + int(inc_val)
    increment = int(inc_val)
    num_elements = ((decades_max - decades_min) / increment)
    decades = [None] * int(num_elements)
    i = 0
    for num in range(decades_min, decades_max, increment):
        decades[i] = num
        i += 1
    return sorted(decades)


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
def buildDecadeTally(directory, decades, increment):
    decade_tally = {}
    for decade in decades:
        try:
            decade_tally[decade] = 0
        except KeyError:
            pass
    for subdir, dirs, files in os.walk(directory):
        for jsondoc in files:
            if jsondoc[0] != ".":
                with open(directory + "/" + jsondoc, 'r', encoding='utf8') as in_file:
                    jsondata = json.load(in_file)
                    year = int(jsondata["4.Year Published"])
                    decade = int(year) - (int(year) % increment)
                    try:
                        decade_tally[decade] += 1
                    except KeyError:
                        pass
    return decade_tally


# take product of tf and idf score
def calculateTF_IDF(idfScore, tfScore):
    tf_idf = tfScore * idfScore
    return tf_idf


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


# returns avg tfidf score for each decade
def tf_idfAvg(decades, keywords, tf_idfResults, increment):
    tf_idf_avg = buildDictOfNums(decades, keywords)
    # Take avg of TFIDF results
    for decade in decades:
        for keyword in keywords:
            length = len(tf_idfResults[decade][keyword])
            total = sum(tf_idfResults[decade][keyword])
            # check if there exist files for the period
            if length > 0 or total > 0:
                try:
                    avg = round((total/length), 4)
                    tf_idf_avg[decade][keyword] = avg
                except ZeroDivisionError:
                    tf_idf_avg[decade][keyword] = 0
            else:
                # no files, use previous period's score
                prev_decade = decade - increment
                try:
                    prev_avg = tf_idf_avg[prev_decade][keyword]
                except KeyError:
                    # case when the first period in the list of dates
                    # has no files associated with it.
                    prev_avg = 0
                tf_idf_avg[decade][keyword] = prev_avg
    return tf_idf_avg


# returns maximum tfidf score for each decade
def tf_idfMax(decades, keywords, tf_idfResults, increment):
    tf_idf_max = buildDictOfNums(decades, keywords)
    # Take max of TFIDF results
    for decade in decades:
        for keyword in keywords:
            try:
                maximum = max(tf_idfResults[decade][keyword])
                tf_idf_max[decade][keyword] = maximum
            except ValueError:
                # no files for this period
                prev_decade = decade - increment
                try:
                    prev_max = tf_idf_max[prev_decade][keyword]
                except KeyError:
                    # case when the first period in the list of dates
                    # has no files associated with it.
                    prev_max = 0
                tf_idf_max[decade][keyword] = prev_max
    return tf_idf_max


# returns minimum tfidf score for each decade
def tf_idfMin(decades, keywords, tf_idfResults, increment):
    tf_idf_min = buildDictOfNums(decades, keywords)
    # Take max of TFIDF results
    for decade in decades:
        for keyword in keywords:
            try:
                minimum = min(tf_idfResults[decade][keyword])
                tf_idf_min[decade][keyword] = minimum
            except ValueError:
                # no files for this period
                prev_decade = decade - increment
                try:
                    prev_min = tf_idf_min[prev_decade][keyword]
                except KeyError:
                    # case when the first period in the list of dates
                    # has no files associated with it.
                    prev_min = 0
                tf_idf_min[decade][keyword] = prev_min
    return tf_idf_min


# calculate term frequency for tfidf
def calculateTF(fdist, w):
    termFreq = fdist[w]
    try:
        maxFreq = fdist[fdist.max()]
        TF = (termFreq/maxFreq)
    except ValueError:
        # Text empty, maxFreq = 0
        TF = 0
    return TF


# calculates term frequency for each keyword/decade pair, then multiplies it
# with the idf score for that decade, yielding a tfidf score for each keyword/document pair.
# The results are stored in a dict, and ordered by decade.
def calculateTF_IDFResults(decades, keywords, directory, idf_results, increment):
    tf_idf_results = buildDictOfLists(decades, keywords)
    for subdir, dirs, files in os.walk(directory):
        for jsondoc in files:
            if jsondoc[0] != ".":
                with open(directory + "/" + jsondoc, 'r', encoding='utf8') as inpt:
                    jsondata = json.load(inpt)
                    text = jsondata["9.Filtered Text"]
                    year = int(jsondata["4.Year Published"])
                    decade = int(year) - (int(year) % increment)
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
def calculateIDFResults(keywords, decades, decade_tally, directory, increment):
    idf_results = buildDictOfNums(decades, keywords)
    for subdir, dirs, files in os.walk(directory):
        for jsondoc in files:
            if jsondoc[0] != ".":
                with open(directory + "/" + jsondoc, 'r', encoding='utf8') as in_file:
                    jsondata = json.load(in_file)
                    text = jsondata["9.Filtered Text"]
                    year = int(jsondata["4.Year Published"])
                    decade = int(year) - (int(year) % increment)
                    fdist = nltk.FreqDist(text)
                    for keyword in keywords:
                        words = keyword.split("/")
                        for w in words:
                            if fdist[w] > 0:
                                try:
                                    idf_results[decade][keyword] += 1
                                    break
                                except KeyError:
                                    pass
                            else:
                                pass
    for decade in decades:
        for keyword in keywords:
            try:
                #Add 1 before logarithm to ensure idf is nonzero
                idf_results[decade][keyword] = \
                    1 + round(math.log((decade_tally[decade]) / idf_results[decade][keyword], 10), 4) \
                        if idf_results[decade][keyword] > 0 else 0
            except KeyError:
                pass
    return idf_results


# returns total word count for each decade
def totalWordCount(decades, directory, increment):
    word_totals = buildSimpleDictOfNums(decades)
    for subdir, dirs, files in os.walk(directory):
        for jsondoc in files:
            if jsondoc[0] != ".":
                with open(directory + "/" + jsondoc, 'r', encoding='utf8') as in_file:
                    jsondata = json.load(in_file)
                    text = jsondata["9.Filtered Text"]
                    words = len(text)
                    year = int(jsondata["4.Year Published"])
                    decade = int(year) - (int(year) % increment)
                    try:
                        word_totals[decade] += words
                    except KeyError:
                        # decade out of range (specified by user)
                        pass
    return word_totals


# returns total keyword count for each keyword/decade pair
def keywordCount(decades, keywords, directory, increment):
    keyword_totals = buildDictOfNums(decades, keywords)
    for subdir, dirs, files in os.walk(directory):
        for jsondoc in files:
            if jsondoc[0] != ".":
                with open(directory + "/" + jsondoc, 'r', encoding='utf8') as in_file:
                    jsondata = json.load(in_file)
                    text = jsondata["9.Filtered Text"]
                    year = int(jsondata["4.Year Published"])
                    decade = year - (year % increment)
                    fdist = nltk.FreqDist(text)
                    for keyword in keywords:
                        words = keyword.split("/")
                        for w in words:
                            word_count = fdist[w]
                            try:
                                keyword_totals[decade][keyword] += word_count
                            except KeyError:
                                # decade out of range (specified by user)
                                pass
    return keyword_totals


# calculates term frequency for each keyword/decade pair as a percentage
# of the total words in all books for each decade
def takeKeywordPercentage(decades, keywords, total_words, keyword_totals, increment):
    keyword_percentages = buildDictOfNums(decades, keywords)
    for decade in decades:
        for keyword in keywords:
            num = keyword_totals[decade][keyword]
            den = total_words[decade]
            if den > 0:
                percent = round((num/den) * 100, 4)
                keyword_percentages[decade][keyword] = percent
            else:
                # no files for this decade, use previous decade's totals
                prev_decade = decade - increment
                try:
                    percent = keyword_percentages[prev_decade][keyword]
                except KeyError:
                    # case when the first period in the list of dates
                    # has no files associated with it.
                    percent = 0
                keyword_percentages[decade][keyword] = percent
    return keyword_percentages


# returns a list of values to be plotted
def buildGraphList(keyword, decades, param):
    i = 0
    a = [0]*len(decades)
    while i < len(decades):
        a[i] += param[decades[i]][keyword]
        i += 1
    return a


# first need a list of all the words for frequency distribution
def obtainWordList(directory, decade, increment):
    word_list = []
    for subdir, dirs, files in os.walk(directory):
        for jsondoc in files:
            if jsondoc[0] != ".":
                with open(directory + "/" + jsondoc, 'r', encoding='utf8') as in_file:
                    jsondata = json.load(in_file)
                    year = int(jsondata["4.Year Published"])
                    d = int(year) - (int(year) % increment)
                    if d == decade:
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
        keywords.append((key_tup[0], round((key_tup[1]/total_words)*100, 4)))
    return keywords


def calculateNWords(decades, directory, num, increment):
    n_dict = buildSimpleDictOfLists(decades)
    for decade in decades:
        word_list = obtainWordList(directory, decade, increment)
        total_words = len(word_list)
        fdist = nltk.FreqDist(word_list)
        n_dict[decade].extend(obtainNWords(fdist, num, total_words))
    return n_dict


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", metavar='in-directory', action="store", help="input directory argument")
    parser.add_argument("-o", help="output file argument", action="store")
    parser.add_argument("-k", help="list of keywords argument, surround list with quotes", action="store")
    parser.add_argument("-dec", help="min/max for year range and incremement value, surround with quotes",
                        action="store")
    parser.add_argument("-t_avg", help="take tf_idf avg for each decade", action="store_true")
    parser.add_argument("-t_max", help="take tf_idf max for each decade", action="store_true")
    parser.add_argument("-t_min", help="take tf_idf min for each decade", action="store_true")
    parser.add_argument("-percent", help="graph word frequency as a percentage of total words (not tfidf)",
                        action="store_true")
    parser.add_argument("-num", help="number of words to grab from each decade, according to whichever metric "
                        "is chosen to be graphed", action="store")

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
    range_years = args.dec.split()
    increment = int(range_years[2])
    # need start date to be evenly divisible by increment value for
    if int(range_years[0]) % increment != 0:
        fail("Make sure the start date is evenly divisible by the increment value.")
    #decades = buildDecadesList(range_years[0], range_years[1])
    decades = buildDecadesList(range_years[0], range_years[1], range_years[2])
    decade_tally = buildDecadeTally(directory, decades, increment)

    # check to make sure only one of the avg/max/min flags are set
    check = []
    check.append(int(args.t_avg)), check.append(int(args.t_max)), \
        check.append(int(args.t_min)), check.append(int(args.percent))
    if sum(check) > 1:
        fail("Please enter a maximum of one of the following arguments: -avg, -max, -min, -percent")

    if args.t_avg or args.t_max or args.t_min or args.percent:
        # build/populate dicts
        idf_results = calculateIDFResults(keywords, decades, decade_tally, directory, increment)
        tf_idf_results = calculateTF_IDFResults(decades, keywords, directory, idf_results, increment)
        # take avg/max/min
        tf_idf_avg = tf_idfAvg(decades, keywords, tf_idf_results, increment)
        tf_idf_max = tf_idfMax(decades, keywords, tf_idf_results, increment)
        tf_idf_min = tf_idfMin(decades, keywords, tf_idf_results, increment)
        # take percent over total words for each keyword
        total_words = totalWordCount(decades, directory, increment)
        keyword_totals = keywordCount(decades, keywords, directory, increment)
        keyword_percentage = takeKeywordPercentage(decades, keywords, total_words, keyword_totals, increment)

    # calculate top N words for each decade, but check if user set -num first
    try:
        n = int(args.num)
        n_dict = calculateNWords(decades, directory, n, increment)
    except TypeError:
        pass

    # create txt file and write all the collected data to it
    out = open(args.o + ".txt", 'w')
    for decade in decades:
        out.write("Decade: " + str(decade) + "\n")
        out.write("Number of books for this decade: " + str(decade_tally[decade]) + "\n")
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


    # determine graph parameters, depending on which flag is set
    if args.t_avg:
        g_max = findMax(keywords, decades, tf_idf_avg)
        g_min = findMin(keywords, decades, tf_idf_avg, g_max)
    if args.t_max:
        g_max = findMax(keywords, decades, tf_idf_max)
        g_min = findMin(keywords, decades, tf_idf_max, g_max)
    if args.t_min:
        g_max = findMax(keywords, decades, tf_idf_min)
        g_min = findMin(keywords, decades, tf_idf_min, g_max)
    if args.percent:
        g_max = findMax(keywords, decades, keyword_percentage)
        g_min = findMin(keywords, decades, keyword_percentage, g_max)

    # plot data according to which of the four flags are set
    for keyword in keywords:
        if args.t_avg:
            plt.plot(decades, buildGraphList(keyword, decades, tf_idf_avg), label=keyword)
        if args.t_max:
            plt.plot(decades, buildGraphList(keyword, decades, tf_idf_max), label=keyword)
        if args.t_min:
            plt.plot(decades, buildGraphList(keyword, decades, tf_idf_min), label=keyword)
        if args.percent:
            plt.plot(decades, buildGraphList(keyword, decades, keyword_percentage), label=keyword)

    # specifies graph params/labels
    if args.t_avg or args.t_max or args.t_min or args.percent:
        plt.legend(bbox_to_anchor=(0, 1.02, 1., .102), loc=3, ncol=int(len(keywords)/2),
                   mode="expand", borderaxespad=0.)
        plt.xlabel("Decade")
        plt.ylabel("Word Frequency")
        if (g_min - .05) < 0:
            plt.axis([int(range_years[0]), int(range_years[1]), 0, g_max + .05])
        else:
            plt.axis([int(range_years[0]), int(range_years[1]), g_min - .05, g_max + .05])
        plt.show()

if __name__ == '__main__':
    main()























