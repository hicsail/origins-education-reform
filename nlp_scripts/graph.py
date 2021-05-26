import argparse, json, os, math, csv
import matplotlib.pyplot as plt
import numpy as np
import common
from PIL import Image
import os


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
            if k != 'label':
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
                    graphed[file]['label'] = jsondata['label']
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


def determine_data_type(statistic):
    mapping = {
        "avg": {
            "data_type": 'tf-idf avg',
            "y_label": "Average TF-IDF",
            "title": "Average TF-IDF Scores Per Period"
        },
        "max": {
            "data_type": 'tf-idf max',
            "y_label": "Maximum TF-IDF",
            "title": "Maximum TF-IDF Scores Per Period"
        },
        "mean": {
            "data_type": 'average frequency',
            "y_label": "Average Frequency",
            "title": "Average Word Frequency Per Period"
        },
        "min": {
            "data_type": 'tf-idf min',
            "y_label": "Minimum TF-IDF",
            "title": "Minimum TF-IDF Scores Per Period"
        }, 
        "percent": {
            "data_type": 'word frequency',
            "y_label": "Word Frequency",
            "title": "Word Frequency as Percentage of Total Words Per Period"
        },
        "var": {
            "data_type": 'variance',
            "y_label": "Variance",
            "title": "Variance of Word Frequency Per Period"
        }
    }
    result = mapping[statistic]
    return (result["data_type"], result["y_label"], result["title"])

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "input",
        help="Input directory path",
        action="store"
    )
    parser.add_argument(
        "statistic",
        help="Statistic to graph",
        choices=["avg", "max", "mean", "min", "percent", "var"],
        action="store"
    )
    parser.add_argument(
        "-output",
        help="Filename for image output",
        action="store"
    )
    parser.add_argument(
        "-bar",
        help="Plot data as a bar graph instead of a line graph",
        action="store_true"
    )
    
    # Breakdown
    parser.add_argument(
        "-breakdown",
        help="breakdown individual keywords",
        action="store_true"
    )

    # Graph Formatting
    parser.add_argument(
        "-bw",
        help="Plots the graph in black-and-white",
        action="store_true"
    )
    parser.add_argument(
        "-barwidth",
        help="Set bar width in bar graph. Requires --bar",
        type=int,
        default=5,
        action="store"
    )
    parser.add_argument(
        "-yaxis",
        help="Set the y-axis range",
        type=int,
        nargs=2,
        action="store"
    )
    parser.add_argument(
        "-padding", 
        help="Set the whitespace on the sides of the graph",
        type=int,
        default=5,
        action="store"
    )
    parser.add_argument(
        "-legendsize",
        help="Set the legend size",
        type=int,
        default=10,
        action="store"
    )
    parser.add_argument(
        "-titlesize",
        help="Set the size of the title",
        type=int,
        default=14,
        action="store"
    )
    parser.add_argument(
        "-labelsize",
        help="Set the size of a tick label",
        type=int,
        default=12,
        action="store"
    )
    parser.add_argument(
        "-axislabelsize",
        help="Set the size of the axis labels",
        type=int,
        default=12,
        action="store"
    )

    args = parser.parse_args()
    if args.barwidth and (args.bar is None):
        parser.error("-barwidth requires --bar.")

    return args

def main():
    args = parse_args()

    global breakdown
    breakdown = args.breakdown

    fig = plt.figure()
    ax1 = plt.subplot2grid((1,1), (0,0))

    (data_type, y_label, title) = determine_data_type(args.statistic)
    
    graph_dict = build_graph_dict(args.input, data_type)

    year_list = build_year_list(args.input)

    if args.yaxis is not None:
        y_params = args.yaxis
    else:
        y_params = find_max_and_min(graph_dict)
        y_params[1] *= 1.2

    # set x-axis
    num_ranges = len(graph_dict)
    if args.bar:
        offset = num_ranges * args.barwidth / 2
    else:
        offset = 0

    index = np.array(sorted(year_list))
    labels = []
    for i in range(len(year_list)):
        start = str(year_list[i])
        end = str(year_list[i + 1])
        labels.append("{0}-{1}".format(start, end))
    plt.xticks(index[1:], labels, fontsize=args.labelsize)

    c = 0
    if args.bar:
        i = 0
        for f in graph_dict:
            for k in graph_dict[f]:
                if k != 'label':
                    if args.bw:
                        color = str(0.3 * c)
                    else:
                        color = np.random.rand(1, 3)
                    ax1.bar(index + (args.barwidth * i) - offset, graph_dict[f][k], args.barwidth, alpha=.8,
                        color=color, label=graph_dict[f]['label'], align='edge')
                    i += 1
            c += 1
    else:
        for f in graph_dict:
            for k in graph_dict[f]:
                if k != 'label':
                    c += 1
                    ax1.plot(index, graph_dict[f][k], label=graph_dict[f]['label'],
                        color="black", linestyle=(0, (2*c, 2*c)))

    # Add title
    plt.title(title, fontsize=args.titlesize)

    # Set axis labels
    plt.xlabel("Period", fontsize=args.axislabelsize)
    plt.ylabel(y_label, fontsize=args.axislabelsize)
    
    # with the bar graph, you want to include the space for the last year in year_list because you need space
    # for the bars. With the line graph, though, you don't want it because all you need is the point.
    diff = year_list[1] - year_list[0]
    ax1.axis([year_list[1] - offset - args.padding, year_list + offset + args.padding, float(y_params[0]), float(y_params[1])])
    
    leg = ax1.legend(prop={'size': args.legendsize})
    leg.get_frame().set_alpha(0.1)

    if args.output:
        plt.savefig(args.o + '.png')
        im = Image.open(args.o + '.png')
        im.save(args.o + '.tiff')
        os.remove(args.o + '.png')
    else:
        plt.show()


if __name__ == '__main__':
    main()
