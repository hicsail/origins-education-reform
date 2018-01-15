import argparse, json
from nlp import config


if __name__ == '__main__':

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
    parser.add_argument('-j', action="store", help='path to json config file', default=None)

    try:
        args = parser.parse_args()
    except IOError:
        pass

    if args.j is None:
        print("hi")
    else:
        args = config.WordFrequencyConfig(args.j)

