import csv, argparse, os
import matplotlib.pyplot as plt
import numpy as np


#                       *** GraphCSV.py ***
#
# This script takes csv files as input (which are themselves output
# of WordFrequency.py or SentAnalysis.py) and graphs whichever information the user
# would like to from them. As of 10/9/16 this script supports graphing for
# the following metrics: tf-idf average, maximum, minimum, term frequency
# as a percentage of total words, and avg/max/min sentiment score.
#


# csv has trouble handling lists explicitly, so need to store
# them as strings and construct lists out of them instead
def string_to_floats(str_inpt):
    str_list = str_inpt.split()
    return_list = []
    for num in str_list:
        return_list.append(float(num))
    return return_list


# find max value in graphed results, used to set graph parameters
def findMax(list_inpt):
    g_max = 0
    for i in range(len(list_inpt)):
        for j in range(len(list_inpt[i][1])):
            if list_inpt[i][1][j] > g_max:
                g_max = list_inpt[i][1][j]
    return g_max


def findMin(list_inpt, g_max):
    g_min = g_max
    for i in range(len(list_inpt)):
        for j in range(len(list_inpt[i][1])):
            if list_inpt[i][1][j] < g_min:
                g_min = list_inpt[i][1][j]
    return g_min


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", help="input csv filepath", action="store")
    parser.add_argument("-avg", help="take tf_idf /sentiment avg for each decade", action="store_true")
    parser.add_argument("-max", help="take tf_idf /sentiment max for each decade", action="store_true")
    parser.add_argument("-min", help="take tf_idf / sentiment min for each decade", action="store_true")
    parser.add_argument("-percent", help="graph word frequency as a percentage of total words (not tfidf)",
                        action="store_true")
    parser.add_argument("-bar", help="plot data as a bar graph (default is line)", action="store_true")
    parser.add_argument("-wf", help="if plotting from word frequency script results", action="store_true")
    parser.add_argument("-sa", help="if plotting from sentiment analysis script results", action="store_true")
    parser.add_argument("-yaxis", help="argument for setting the y-axis min/max values", action="store")

    try:
        args = parser.parse_args()
    except IOError:
        pass

    # list of tuples - (keyword, stats_list)
    graphed = []

    # iterate over directory of csv files
    for subdir, dirs, files in os.walk(args.i):
        for csv_file in files:
            if csv_file[0] != "." and csv_file[-4:] == ".csv":
                # construct list of tuples to be graphed (word, list)
                with open(args.i + "/" + csv_file, 'r', encoding='UTF-8') as csvfile:
                    read_csv = csv.reader(csvfile, delimiter=',')
                    year_list = []
                    # graph results from WordFrequency.py
                    if args.wf:
                        for row in read_csv:
                            if row[0] == "word" and row[1] == "tf-idf avg":
                                years = row[5].split()
                                for year in years:
                                    year_list.append(int(year))
                            else:
                                if args.avg:
                                    graphed.append((row[0], string_to_floats(row[1])))
                                if args.max:
                                    graphed.append((row[0], string_to_floats(row[2])))
                                if args.min:
                                    graphed.append((row[0], string_to_floats(row[3])))
                                if args.percent:
                                    graphed.append((row[0], string_to_floats(row[4])))
                    # graph results from SentAnalysis.py
                    if args.sa:
                        for row in read_csv:
                            if row[0] == "word" and row[1] == "sent avg":
                                # list of periods
                                years = row[5].split()
                                # number of documents for each period
                                docs = row[6].split()
                                for year in years:
                                    year_list.append(int(year))
                            elif row[0] == "Average Sentiment Across Corpus":
                                graphed.append((row[0], string_to_floats(row[1])))
                            else:
                                if args.avg:
                                    graphed.append((row[0], string_to_floats(row[1])))
                                if args.max:
                                    graphed.append((row[0], string_to_floats(row[2])))
                                if args.min:
                                    graphed.append((row[0], string_to_floats(row[3])))

    try:
        y_vals = args.yaxis.split()
    except AttributeError:
        # determine maximum y-coordinate
        tmp_max = findMax(graphed)
        g_max = tmp_max + float(tmp_max/8)
        tmp_min = findMin(graphed, tmp_max)
        g_min = tmp_min - float(tmp_min/8)
        y_vals = [g_min, g_max]

    # set x-axis
    index = np.array(sorted(year_list))
    if args.bar:
        last = len(year_list) - 1
        # make bar width equal to the length of the x-axis divided by how many bars will be drawn
        bar_width = (int(year_list[last] - year_list[0]) / (len(year_list) * len(graphed)))
        opacity = .8
        # plot each list of values which correspond to a particular keyword's stats
        for i in range(len(graphed)):
            plt.bar(index + (bar_width * i), graphed[i][1], bar_width, alpha=opacity,
                    color=np.random.rand(3, 1), label=graphed[i][0])
    else:
        # plot each list of values which correspond to a particular keyword's stats, specific to line graphs
        for i in range(len(graphed)):
            plt.plot(year_list, graphed[i][1], label=graphed[i][0])

    # labels etc.
    plt.xlabel("Period")
    if args.wf:
        plt.ylabel("Word Frequency")
    if args.sa:
        plt.ylabel("Sentiment Score")

    if args.wf:
        # titles corresponding to WordFrequency.py metrics
        if args.avg:
            plt.title("TF-IDF Average Scores Per Period")
        if args.max:
            plt.title("TF-IDF Maximum Scores Per Period")
        if args.min:
            plt.title("TF-IDF Minimum Scores Per Period")
        if args.percent:
            plt.title("Word Frequency as Percentage of Total Words Per Period")
    if args.sa:
        # titles corresponding to SentAnalysis.py metrics
        if args.avg:
            plt.title("Average Sentiment Scores Per Period")
        if args.max:
            plt.title("Maximum Sentiment Scores Per Period")
        if args.min:
            plt.title("Minimum Sentiment Scores Per Period")

    # generate x-tick labels for x-axis
    labels = []
    for i in range(len(year_list) - 1):
        start = str(year_list[i])
        end = str(year_list[i + 1])
        labels.append("{0}-{1}".format(start, end))
    plt.xticks(index, labels)

    # only different because with the bar graph, you want to include the space for the last year in year_list (i.e. -
    # the end of the last period being counted) because you need space for the bars. With the line graph, though, you
    # don't want it because it just flatlines there; all you need is the point.
    if args.bar:
        plt.axis([year_list[0], year_list[len(year_list) - 1], float(y_vals[0]), float(y_vals[1])])
    else:
        plt.axis([year_list[0], year_list[len(year_list) - 2], float(y_vals[0]), float(y_vals[1])])
    plt.legend()
    plt.show()

if __name__ == '__main__':
    main()
