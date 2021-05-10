import argparse, json, os, math, csv
import matplotlib.pyplot as plt
import numpy as np
import common


# csv has trouble handling lists explicitly, so need to store
# them as strings and construct lists out of them instead
def string_to_floats(str_inpt):
    str_list = str_inpt.split()
    return_list = []
    for num in str_list:
        return_list.append(float(num))
    return return_list


# find max and min values from graphed dict
def find_max_and_min(in_dict):
    g_max = 0
    g_min = math.inf
    for f in in_dict:
        for k in in_dict[f]:
            if k != 'nation':
                for i in range(len(in_dict[f][k])):
                    if in_dict[f][k][i] > g_max:
                        g_max = in_dict[f][k][i]
                    if in_dict[f][k][i] < g_min:
                        g_min = in_dict[f][k][i]
    return [g_min, g_max]


# builds dictionary of graphed values from directory of json files and metric to be graphed
def build_graph_dict(in_dir, data_type):
    graphed = {}
    # determine index of data for csv files
    indx = determine_index(data_type)
    # iterate over json / csv files in directory, append
    # data from each to keyword entry in graphed dict
    for _, _, files in os.walk(in_dir):
        for file in files:
            if file[0] != '.' and file[-5:] == '.json':
                with open(in_dir + "/" + file, 'r', encoding='utf8') as in_file:
                    jsondata = json.load(in_file)
                    keywords = jsondata['keywords']
                    graphed[file] = {}
                    graphed[file]['nation'] = jsondata['nation']
                    for keyword in keywords:
                        if not breakdown:
                            # this step assumes there are no keyword repeats across files
                            graphed[file][keyword] = [0]
                            graphed[file][keyword].extend(jsondata[keyword][data_type])
                        else:
                            for k in keyword.split('/'):
                                # only works for keyword percentages
                                graphed[file][k] = [0]
                                graphed[file][k].extend(jsondata['breakdown'][k])
            elif file[0] != '.' and file[-4:] == '.csv':
                # hacky bc csv files are awful
                with open(in_dir + "/" + file, 'r', encoding='utf8') as in_file:
                    read_csv = csv.reader(in_file, delimiter=',')
                    for row in read_csv:
                        if row[0] != "word" and row[1] != "tf-idf avg":
                            graphed[row[0]] = []
                            graphed[row[0]].extend(string_to_floats(row[indx]))
    return graphed


# determine column index for data in csv files
def determine_index(data_type):
    index = 0
    if data_type == 'tf-idf avg':
        index = 1
    elif data_type == 'tf-idf max':
        index = 2
    elif data_type == 'tf-idf min':
        index = 3
    elif data_type == 'word frequency':
        index = 4
    elif data_type == 'average frequency':
        index = 5
    elif data_type == 'variance':
        index = 6
    else:
        common.fail('You shouldn\'t be able to get here, congratulations!!')
    return index


# checks to make sure the year lists in each json / csv file are equal
def build_year_list(in_dir):
    year_lists = []
    for subdir, dirs, files in os.walk(in_dir):
        for file in files:
            if file[0] != '.' and file[-5:] == '.json':
                with open(in_dir + "/" + file, 'r', encoding='utf8') as in_file:
                    jsondata = json.load(in_file)
                    year_lists.append(sorted(jsondata['year list']))
            elif file[0] != '.' and file[-4] == '.csv':
                with open(in_dir + "/" + file, 'r', encoding='utf8') as in_file:
                    read_csv = csv.reader(in_file, delimiter=',')
                    for row in read_csv:
                        if row[0] == "word" and row[1] == "tf-idf avg":
                            years = row[7].split()
                            year_list = sorted([int(year) for year in years])
                            year_lists.append(year_list)
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
            width = float(width)
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
    parser.add_argument("-b_width", help="manually set bar width, default is 5", action="store")
    parser.add_argument("-breakdown", help="breakdown individual keywords", action="store_true")
    parser.add_argument("-padding", help="Set the whitespace on the sides of the graph", action="store")

    parser.add_argument("-leg", help="manually set size of legend, default is 10", action="store")
    parser.add_argument("-titlesize", help="Set the size of the title", action="store")
    parser.add_argument("-labelsize", help="Set the size of a tick label", action="store")
    parser.add_argument("-axislabelsize", help="Set the size of the axis labels", action="store")

    try:
        args = parser.parse_args()
    except IOError:
        common.fail("IO Error While Parsing Arguments")

    global breakdown

    if args.breakdown:
        breakdown = True
    else:
        breakdown = False

    fig = plt.figure()
    ax1 = plt.subplot2grid((1,1), (0,0))

    args_params = determine_data_type(
        args.avg, args.max, args.min, args.percent, args.mean, args.var)
    data_type, y_label, title = args_params[0], args_params[1], args_params[2]

    graph_dict = build_graph_dict(args.i, data_type)

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
        y_params[1] *= 1.2

    # set x-axis
    num_ranges = len(graph_dict)
    if bar:
        offset = num_ranges * width / 2
    else:
        offset = 0

    index = np.array(sorted(year_list)[1:])
    labels = []
    for i in range(len(year_list) -1):
        start = str(year_list[i])
        end = str(year_list[i + 1])
        labels.append("{0}-{1}".format(start, end))
    plt.xticks(index, labels)
    if args.labelsize:
        for label in ax1.xaxis.get_ticklabels():
            label.set_size(args.labelsize)

    if bar:
        i = 0
        for f in graph_dict:
            for k in graph_dict[f]:
                if k != 'nation':
                    ax1.bar(index + (width * i) - offset, graph_dict[f][k][2:], width, alpha=.8,
                            color=np.random.rand(1, 3), label="{0}: {1}".format(f,k), align='edge')
                    i += 1
    else:
        for f in graph_dict:
            for k in graph_dict[f]:
                if k != 'nation':
                    ax1.plot(index, graph_dict[f][k][2:], label="{0}: {1}".format(f,k))

    # Add title
    if args.titlesize:
        plt.title(title, fontsize=args.titlesize)
    else:
        plt.title(title)

    # Set axis labels
    if args.axislabelsize:
        plt.xlabel("Period", fontsize=args.axislabelsize)
        plt.ylabel(y_label, fontsize=args.axislabelsize)
    else:
        plt.xlabel("Period")
        plt.ylabel(y_label)

    if args.padding:
        padding = int(args.padding)
    else:
        padding = 5

    diff = year_list[1] - year_list[0]
    ax1.axis([year_list[1] - offset - padding, year_list[-1] + offset + padding, float(y_params[0]), float(y_params[1])])
    
    leg = ax1.legend(prop={'size': leg_size})
    leg.get_frame().set_alpha(0.1)
    plt.show()


if __name__ == '__main__':
    main()