import csv, argparse
import matplotlib.pyplot as plt
import numpy as np


#                       *** GraphCSV.py ***
#
# This script takes csv files as input (which are themselves output
# of WordFrequencyScript.py) and graphs whichever information the user
# would like to from them. As of 9/1/16 this script supports graphing for
# the following metrics: tf-idf average, maximum, minimum, and term frequency
# as a percentage of total words.
#


# csv has trouble handling lists explicitly, so need to store
# them as strings and construct lists out of them instead
def string_to_floats(str_inpt):
    str_list = str_inpt.split()
    return_list = []
    for num in str_list:
        return_list.append(float(num))
    return return_list


# find max value used in graphed results
def findMax(list_inpt):
    g_max = 0
    for i in range(len(list_inpt)):
        for j in range(len(list_inpt[i][1])):
            if list_inpt[i][1][j] > g_max:
                g_max = list_inpt[i][1][j]
    return g_max


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", help="input csv filepath", action="store")
    parser.add_argument("-t_avg", help="take tf_idf avg for each decade", action="store_true")
    parser.add_argument("-t_max", help="take tf_idf max for each decade", action="store_true")
    parser.add_argument("-t_min", help="take tf_idf min for each decade", action="store_true")
    parser.add_argument("-percent", help="graph word frequency as a percentage of total words (not tfidf)",
                        action="store_true")
    parser.add_argument("-bar", help="plot data as a bar graph (default is line)", action="store_true")

    try:
        args = parser.parse_args()
    except IOError:
        pass

    # list of tuples - (keyword, stats_list)
    graphed = []

    # construct list of tuples to be graphed (word, list)
    with open(args.i + ".csv", encoding='UTF-8') as csvfile:
        read_csv = csv.reader(csvfile, delimiter=',')
        year_list = []
        for row in read_csv:
            if row[0] == "word" and row[1] == "tf-idf avg":
                years = row[5].split()
                for year in years:
                    year_list.append(int(year))
            # all these np arrays here are lists, need to be ints. do later because its fucking up
            else:
                if args.t_avg:
                    graphed.append((row[0], string_to_floats(row[1])))
                if args.t_max:
                    graphed.append((row[0], string_to_floats(row[2])))
                if args.t_min:
                    graphed.append((row[0], string_to_floats(row[3])))
                if args.percent:
                    graphed.append((row[0], string_to_floats(row[4])))

    # determine maximum y-coordinate
    g_max = findMax(graphed)
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
    plt.ylabel("Word Frequency")
    if args.t_avg:
        plt.title("TF-IDF Average Scores Per Period")
    if args.t_max:
        plt.title("TF-IDF Maximum Scores Per Period")
    if args.t_min:
        plt.title("TF-IDF Minimum Scores Per Period")
    if args.percent:
        plt.title("Word Frequency as Percentage of Total Words Per Period")

    # generate x-tick labels for x-axis
    labels = []
    for i in range(len(year_list) - 1):
        start = str(year_list[i])
        end = str(year_list[i + 1])
        labels.append("{0}-{1}".format(start, end))
    plt.xticks(index, labels)

    # only different because with the bar graph, you want to include the space for the last year in year_list (i.e. -
    # the end of the last period being counted) because you need space for the bars. With the line graph, though, you
    # don't want it because it just flatlines there - all you need is the point.
    if args.bar:
        plt.axis([year_list[0], year_list[len(year_list) - 1], 0, g_max + (g_max/8)])
    else:
        plt.axis([year_list[0], year_list[len(year_list) - 2], 0, g_max + (g_max/8)])
    plt.legend()
    plt.show()

if __name__ == '__main__':
    main()
