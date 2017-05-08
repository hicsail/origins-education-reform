import argparse, json, os, common, math
import matplotlib.pyplot as plt
import numpy as np


# find max and min values from graphed dict
def find_max_and_min(in_dict):
    g_max = 0
    g_min = math.inf
    for k in in_dict:
        for i in range(len(in_dict[k])):
            if in_dict[k][i] > g_max:
                g_max = in_dict[k][i]
            if in_dict[k][i] < g_min:
                g_min = in_dict[k][i]
    return [g_min, g_max]


# builds dictionary of graphed values from directory of json files and metric to be graphed
def build_graph_dict(in_dir, data_type):
    graphed = {}
    numdocs = []
    # iterate over jsonfiles in directory, append
    # data from each to keyword entry in graphed dict
    for subdir, dirs, files in os.walk(in_dir):
        for jfile in files:
            if jfile[0] != '.' and jfile[-5:] == '.json':
                with open(in_dir + "/" + jfile, 'r', encoding='utf8') as in_file:
                    jsondata = json.load(in_file)
                    keywords = jsondata['keywords']
                    numdocs.append(jsondata['number of documents'])
                    for keyword in keywords:
                        graphed[keyword] = []
                        graphed[keyword].extend(jsondata[keyword][data_type])
    return [graphed, numdocs]


# checks to make sure the year lists in each json file are equal
def build_year_list(in_dir):
    year_lists = []
    for subdir, dirs, files in os.walk(in_dir):
        for jfile in files:
            if jfile[0] != '.' and jfile[-5:] == '.json':
                with open(in_dir + "/" + jfile, 'r', encoding='utf8') as in_file:
                    jsondata = json.load(in_file)
                    year_lists.append(jsondata['year list'])
    for year_list in year_lists:
        if year_list != year_lists[0]:
            common.fail("One of your files has a different year list from the others." +
                        " Please make sure all your files contain the same year lists.")
    # just return first list in year_lists if they're all the same
    return year_lists[0]


def determine_data_type(tavg, tmax, tmin, percent, mean, var):
    # init return values so IDE doesn't complain
    data_type, y_label, title = '', '', ''
    arg_sum = int(tavg) + int(tmax) + int(tmin) + int(percent) + int(mean) + int(var)
    if arg_sum > 1 or arg_sum < 1:
        common.fail("Please enter exactly one graphing parameter.")
    else:
        if tavg:
            data_type = 'tf-idf avg'
            y_label = "Average TF-IDF"
            title = "Average TF-IDF Scores Per Period"
        elif tmax:
            data_type = 'tf-idf max'
            y_label = "Maximum TF-IDF"
            title = "Maximum TF-IDF Scores Per Period"
        elif tmin:
            data_type = 'tf-idf min'
            y_label = "Minimum TF-IDF"
            title = "Minimum TF-IDF Scores Per Period"
        elif percent:
            data_type = 'word frequency'
            y_label = "Word Frequency"
            title = "Word Frequency as Percentage of Total Words Per Period"
        elif mean:
            data_type = 'average frequency'
            y_label = "Average Frequency"
            title = "Average Word Frequency Per Period"
        elif var:
            data_type = 'variance'
            y_label = "Variance"
            title = "Variance of Word Frequency Per Period"
        else:
            common.fail('You shouldn\'t be able to get here, congratulations!!')
    return [data_type, y_label, title]


# if bar, determine bar width
def plot_type(bar, width):
    if bar:
        if width is not None:
            width = width
        else:
            width = 5
    return [bar, width]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", help="input directory path", action="store")
    parser.add_argument("-avg", help="take tf_idf /sentiment avg for each decade", action="store_true")
    parser.add_argument("-max", help="take tf_idf /sentiment max for each decade", action="store_true")
    parser.add_argument("-min", help="take tf_idf / sentiment min for each decade", action="store_true")
    parser.add_argument("-percent", help="graph word frequency as a percentage of total words (not tfidf)",
                        action="store_true")
    parser.add_argument("-mean", help="display arithmetic mean", action="store_true")
    parser.add_argument("-var", help="display variance", action="store_true")
    parser.add_argument("-bar", help="plot data as a bar graph (default is line)", action="store_true")
    parser.add_argument("-yaxis", help="argument for setting the y-axis min/max values", action="store")
    parser.add_argument("-b_width", help="manually set bar width, default is .8", action="store")
    parser.add_argument("-leg", help="manually set size of legend, default is 10", action="store")

    try:
        args = parser.parse_args()
    except IOError:
        common.fail("IO Error While Parsing Arguments")

    fig = plt.figure()
    ax1 = plt.subplot2grid((1,1), (0,0))

    args_params = determine_data_type(
        args.avg, args.max, args.min, args.percent, args.mean, args.var)
    data_type, y_label, title = args_params[0], args_params[1], args_params[2]

    graph_params = build_graph_dict(args.i, data_type)
    graph_dict, numdocs = graph_params[0], graph_params[1]

    year_list = build_year_list(args.i)

    plot_params = plot_type(args.bar, args.b_width)
    bar, width = plot_params[0], plot_params[1]

    if args.leg is not None:
        leg_size = int(args.leg)
    else:
        leg_size = 10

    if args.yaxis is not None:
        y_params = args.yaxis.split()
    else:
        y_params = find_max_and_min(graph_dict)

    # set x-axis
    index = np.array(sorted(year_list))
    labels = []
    for i in range(len(year_list) - 1):
        start = str(year_list[i])
        end = str(year_list[i + 1])
        current_numdocs = ''
        for j in range(len(numdocs)):
            current_numdocs += str(numdocs[j][i]) + " "
        labels.append("{0}-{1} \n Docs: {2}".format(start, end, current_numdocs))
    plt.xticks(index, labels)
    for label in ax1.xaxis.get_ticklabels():
        label.set_rotation(-25)
        label.set_size(7)

    if bar:
        i = 0
        for k in graph_dict:
            ax1.bar(index + (width * i), graph_dict[k], width, alpha=.8,
                    color=np.random.rand(3, 1), label=k)
            i += 1
    else:
        for k in graph_dict:
            ax1.plot(index, graph_dict[k], label=k)

    # labels etc.
    plt.xlabel("Period")
    plt.ylabel(y_label)
    plt.title(title)

    # with the bar graph, you want to include the space for the last year in year_list because you need space
    # for the bars. With the line graph, though, you don't want it because all you need is the point.
    if args.bar:
        ax1.axis([year_list[0], year_list[len(year_list) - 1], float(y_params[0]), float(y_params[1])])
    else:
        ax1.axis([year_list[0], year_list[len(year_list) - 2], float(y_params[0]), float(y_params[1])])

    leg = ax1.legend(prop={'size': leg_size})
    leg.get_frame().set_alpha(0.1)
    plt.show()


if __name__ == '__main__':
    main()