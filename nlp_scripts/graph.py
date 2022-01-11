import argparse, json, os, math
import matplotlib.pyplot as plt
import numpy as np
import common

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
    # iterate over json files in directory, append
    # data from each to keyword entry in graphed dict
    for _, _, files in os.walk(in_dir):
        for file in files:
            if file[0] == '.':
                continue
            if file[-5:] != '.json':
                continue
            with open(in_dir + "/" + file, 'r', encoding='utf8') as in_file:
                jsondata = json.load(in_file)
                keywords = jsondata['keywords']
                graphed[file] = {}
                graphed[file]['label'] = jsondata['label']
                for keyword in keywords:
                    if not breakdown:
                        # this step assumes there are no keyword repeats across files
                        graphed[file][keyword] = []
                        graphed[file][keyword].extend(jsondata[keyword][data_type])
                    else:
                        for k in keyword.split('/'):
                            # only works for keyword percentages
                            graphed[file][k] = []
                            graphed[file][k].extend(jsondata['breakdown'][k])
    return graphed

# checks to make sure the year lists in each json file are equal
def build_year_list(in_dir):
    year_lists = []
    for subdir, dirs, files in os.walk(in_dir):
        for file in files:
            if file[0] == '.':
                continue
            if file[-5:] != '.json':
                continue
            with open(in_dir + "/" + file, 'r', encoding='utf8') as in_file:
                jsondata = json.load(in_file)
                year_lists.append(sorted(jsondata['year list']))
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
    return result["data_type"], result["y_label"], result["title"]

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i",
        help="Input directory path",
        action="store"
    )
    parser.add_argument(
        "-stat",
        help="Statistic to graph",
        choices=["avg", "max", "mean", "min", "percent", "var"],
        action="store"
    )
    parser.add_argument(
        "-o",
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
        "-b_width",
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
        "-leg",
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
    if args.b_width and (args.bar is None):
        parser.error("-b_width requires --bar.")

    return args

def main():
    args = parse_args()

    global breakdown

    if args.breakdown:
        breakdown = True
    else:
        breakdown = False

    fig = plt.figure()
    ax1 = plt.subplot2grid((1,1), (0,0))

    data_type, y_label, title = determine_data_type(args.stat)

    graph_dict = build_graph_dict(args.i, data_type)

    year_list = build_year_list(args.i)

    if args.b_width is not None:
        width = float(args.b_width)
    else:
        width = 5

    if args.leg is not None:
        leg_size = int(args.leg)
    else:
        leg_size = 10

    if args.yaxis is not None:
        y_params = args.yaxis.split()
    else:
        y_params = find_max_and_min(graph_dict)
        y_params[0] = 0
        y_params[1] *= 1.2

    # set x-axis
    num_ranges = len(graph_dict)
    if args.bar:
        offset = num_ranges * width / 2
    else:
        offset = 0

    year_list = sorted(year_list)
    index = np.array(sorted(year_list)[:-1])
    diff = index[1] - index[0]
    ticks = index - diff
    labels = ["{0}-{1}".format(year_list[i], year_list[i+1]) for i in range(len(year_list) - 1)]
    plt.xticks(index, labels)
    if args.labelsize:
        for label in ax1.xaxis.get_ticklabels():
            label.set_size(args.labelsize)

    if args.bar:
        i = 0
        for f in graph_dict:
            for k in graph_dict[f]:
                if k != 'label':
                    print(index)
                    print(graph_dict[f][k])
                    ax1.bar(index + (width * i) - offset, graph_dict[f][k], width, alpha=.8,
                            color=np.random.rand(1, 3), label="{0}: {1}".format(f,k), align='edge')
                    i += 1
    else:
        for f in graph_dict:
            for k in graph_dict[f]:
                if k != 'label':
                    print(index)
                    print(graph_dict[f][k])
                    ax1.plot(index, graph_dict[f][k], label="{0}: {1}".format(f,k))

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

    ax1.axis([index[0] - offset - padding, index[-1] + offset + padding, float(y_params[0]), float(y_params[1])])
    
    leg = ax1.legend(prop={'size': leg_size})
    leg.get_frame().set_alpha(0.1)
    plt.show()


if __name__ == '__main__':
    main()