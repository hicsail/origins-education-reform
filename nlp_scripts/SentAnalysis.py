import os, argparse, json, csv, tqdm
from afinn import Afinn
import common


#                                       *** SentAnalysis.py ***
#
#   This script takes the directory created by SentBuilder.py (which outputs a directory and subdirectories
# corresponding to a list of keywords) and calculates sentiment scores on them corresponding to the AFINN
# word list (http://www2.imm.dtu.dk/pubdb/views/publication_details.php?id=6010). It creates a text file which
# lists those scores, along with which documents per period had the highest and lowest sentiment scores. It also
# creates a csv file with lists corresponding to avg/max/min sentiment scores per period, which can then be
# passed to GraphCSV.py as input.
#


# build list of keywords
def build_key_list(directory):
    key_list = []
    for dirs, subdirs, files in os.walk(directory):
        for subdir in subdirs:
            key_list.append(subdir)
    return key_list


# sort dict entries in a list of tuples by second value (i.e. - sentiment score)
def sort_sent_dict(year_list, key_list, sent_results):
    for year in year_list:
        for keyword in key_list:
            sent_results[year][keyword] = sorted(sent_results[year][keyword], key=lambda x: x[1])
    return sent_results


# build dict needed to calculate average sentiment across corpus, per N words
def populate_overall_sentiment(directory, overall_list, year_list, afinn):
    overall_sent = common.build_dict_of_lists(year_list, overall_list)
    for subdir, dirs, files in os.walk(directory):
        print("Calculating sentiment across entire corpus.")
        for jsondoc in tqdm.tqdm(files):
            if jsondoc[0] == ".":
                continue
            with open(directory + "/" + jsondoc, 'r', encoding='utf8') as inpt:
                sentiment = 0
                jsondata = json.load(inpt)
                text = jsondata["Filtered Text"]
                year = int(jsondata["Year"])
                # check to make sure it's within range specified by user
                if year < yrange_min or year >= yrange_max:
                    continue
                # determine which period it falls within
                target = common.determine_year(year, year_list)
                for i in range(len(text)):
                    sentiment += afinn.score(text[i])
                    # even though overall_list only has one keyword, this looks
                    # better than just hard-coding "all" within the method
                truncated_sentiment = float(sentiment/len(text))
                for keyword in overall_list:
                    # append entry as tuple rather than just sentiment score
                    # so I can use sent_calcs to get average
                    overall_sent[target][keyword].append((jsondoc, truncated_sentiment))
    return overall_sent


# determines the length of the pieces of extracted text. used to truncate the overall_sent
# calculations to reflect average sentiment per N words (with N = length of extracted text),
# rather than average sentiment across an entire document.
def determine_text_length(directory):
    for dirs, subdirs, files in os.walk(directory):
        for subdir in subdirs:
            for folders, subfolders, files in os.walk(dirs + "/" + subdir):
                for jsondoc in files:
                    if jsondoc[0] == ".":
                        continue
                    with open(dirs + "/" + subdir + "/" + jsondoc, 'r', encoding='utf8') as inpt:
                        jsondata = json.load(inpt)
                        text = jsondata["Words"]
                        length = len(text)
                        return length

# fill sent dict with sent results for each json doc w/r/t AFINN dict
def populate_sent_dict(directory, key_list, year_list, afinn):
    sent_dict = common.build_dict_of_lists(year_list, key_list)
    for dirs, subdirs, files in os.walk(directory):
        # 'subdir' corresponds to a keyword
        for subdir in subdirs:
            for folders, subfolders, file in os.walk(dirs + "/" + subdir):
                for jsondoc in file:
                    if jsondoc[0] != ".":
                        with open(dirs + "/" + subdir + "/" + jsondoc, 'r', encoding='utf8') as inpt:
                            sentiment = 0
                            jsondata = json.load(inpt)
                            text = jsondata["Text"]
                            year = int(jsondata["Year"])
                            # check to make sure it's within range specified by user
                            if yrange_min <= year < yrange_max:
                                target = common.determine_year(year, year_list)
                                sentiment += afinn.score(text)
                                sent_dict[target][subdir].append((jsondoc, sentiment))
    sent_dict_sorted = sort_sent_dict(year_list, key_list, sent_dict)
    return sent_dict_sorted


# sometimes a period has no json documents associated with it. it makes the graph look
# bad and throws a ValueError, so this method makes that period's score equal to the
# period directly before it.
def handle_empty_entry(year_list, i, keyword, sent_result):
    # no files for this period
    prev_year = year_list[i - 1]
    try:
        previous = sent_result[prev_year][keyword]
    except KeyError:
        # case when the first period in the list of dates
        # has no files associated with it.
        previous = 0
    return previous


# builds dicts for avg, max, and min sentiment scores. type of
# score that gets calculated is inputted as the 'type' argument.
def sent_calcs(year_list, key_list, sent_results, calc_type):
    sent_result = common.build_dict_of_nums(year_list, key_list)
    print("Calculating average, max, and min sentiment scores.")
    for i in tqdm.tqdm(range(len(year_list))):
        for keyword in key_list:
            length = len(sent_results[year_list[i]][keyword])
            if calc_type == "max":
                try:
                    maximum = sent_results[year_list[i]][keyword][length - 1][1]
                    sent_result[year_list[i]][keyword] = maximum
                except (ValueError, IndexError) as e:
                    # no files for this period
                    sent_result[year_list[i]][keyword] = handle_empty_entry(year_list, i, keyword, sent_result)
            if calc_type == "min":
                try:
                    minimum = sent_results[year_list[i]][keyword][0][1]
                    sent_result[year_list[i]][keyword] = minimum
                except (ValueError, IndexError) as e:
                    # no files for this period
                    sent_result[year_list[i]][keyword] = handle_empty_entry(year_list, i, keyword, sent_result)
            if calc_type == "avg":
                totals = []
                for j in range(length):
                    totals.append(sent_results[year_list[i]][keyword][j][1])
                total = sum(totals)
                # make sure there are files associated with this period
                if length > 0:
                    sent_result[year_list[i]][keyword] = round((total / length), 4)
                elif total > 0:
                    sent_result[year_list[i]][keyword] = 0
                else:
                    # no files for this period / keyword pair, use previous period's score
                    sent_result[year_list[i]][keyword] = handle_empty_entry(year_list, i, keyword, sent_result)
            # kept total in here just in case we figure out some way of normalizing the results
            if calc_type == "total":
                totals = []
                for j in range(length):
                    totals.append(sent_results[year_list[i]][keyword][j][1])
                total = sum(totals)
                sent_result[year_list[i]][keyword] = total
    return sent_result

# can't store lists in csv file, so need to store data in string
def list_to_string(list_inpt):
    return_string = ""
    for wd in list_inpt:
        return_string += (str(wd) + " ")
    return return_string

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", metavar='in-dir', action="store", help="input directory argument")
    parser.add_argument("-c", help="file path to full corpus", action="store")
    parser.add_argument("-y", help="min/max for year range and increment value, surround with quotes",
                        action="store")
    parser.add_argument("-num", help="number of max/min documents to grab from each period", action="store")
    parser.add_argument("-p", help="boolean to analyze by different periods rather than a fixed increment value",
                        action="store_true")
    parser.add_argument("-csv", help="file path to csv output", action="store")
    parser.add_argument("-txt", help="file path to txt output", action="store")
    parser.add_argument("-language", help="language for AFINN word list. \'en\' for english, "
                                          "\'da\' for danish", action="store")

    try:
        args = parser.parse_args()
    except IOError:
        pass

    global periods, yrange_min, yrange_max

    periods = args.p
    directory = args.i
    corpus_path = args.c

    range_years = args.y.split()
    year_params = common.year_params(range_years, periods)
    increment, yrange_min, yrange_max = year_params[0], year_params[1], year_params[2]

    # initialize list of years and dict to keep track of
    # how many books between each year range
    year_list = common.build_year_list(increment, range_years, periods, yrange_max, yrange_min)

    # set up dicts for sentiment word list, keyword list, & results of sentiment analysis
    # 'en' == english, 'da' == danish
    afinn = Afinn(language=args.language.lower())
    key_list = build_key_list(directory)
    overall_list = ["Average Sentiment Across Corpus"]

    # master dict with raw sent scores and their corresponding json doc file names
    sent_results = populate_sent_dict(directory, key_list, year_list, afinn)
    overall_sent = populate_overall_sentiment(corpus_path, overall_list, year_list, afinn)

    # individual sentiment score calculations
    sent_avg = sent_calcs(year_list, key_list, sent_results, "avg")
    sent_min = sent_calcs(year_list, key_list, sent_results, "min")
    sent_max = sent_calcs(year_list, key_list, sent_results, "max")
    sent_total = sent_calcs(year_list, key_list, sent_results, "total")
    overall_avg = sent_calcs(year_list, overall_list, overall_sent, "avg")

    # create txt file and write all the collected data to it
    with open(args.txt + '.txt', 'w') as txt_out:
        txt_out.write("Corresponding CSV file for this text document is located on your machine at the "
                      "following filepath: {0}".format(args.csv) + "\n")
        for i in range(len(year_list) - 1):
            txt_out.write("Period: {0} - {1}".format(str(year_list[i]), str(year_list[i+1])) + "\n")
            for keyword in overall_list:
                txt_out.write("Average sentiment score across the corpus for this period: {0}"
                              .format(str(overall_avg[year_list[i]][keyword])) + "\n")
            for keyword in key_list:
                txt_out.write("{0}:".format(str(keyword)) + "\n")
                txt_out.write("Number of documents for this period/keyword pair: {0}"
                              .format(str(len(sent_results[year_list[i]][keyword]))) + "\n")
                txt_out.write("Avg Sentiment score for {0} in this period: {1}"
                              .format(keyword, str(sent_avg[year_list[i]][keyword]) + "\n"))
                txt_out.write("Max Sentiment score for {0} in this period: {1}"
                              .format(keyword, str(sent_max[year_list[i]][keyword]) + "\n"))
                txt_out.write("Min Sentiment score for {0} in this period: {1}"
                              .format(keyword, str(sent_min[year_list[i]][keyword]) + "\n"))
                try:
                    common.list_max_docs(txt_out, year_list[i], keyword, sent_results, args.num, "sentiment")
                    common.list_min_docs(txt_out, year_list[i], keyword, sent_results, args.num, "sentiment")
                except (AttributeError, UnboundLocalError, TypeError) as e:
                    # user didn't want max/min n words
                    pass
            txt_out.write("\n")

    # create a csv file and write sentiment scores to it
    with open(args.csv + '.csv', 'w', newline='', encoding='utf-8') as csv_out:
        csvwriter = csv.writer(csv_out, delimiter=',')
        year_list_str = []
        num_docs_str = []
        for year in year_list:
            year_list_str.append(str(year))
            for keyword in key_list:
                num_docs_str.append(str(len(sent_results[year][keyword])))
        year_string = " ".join(year_list_str)
        num_docs_string = " ".join(num_docs_str)

        csvwriter.writerow(['word', 'sent avg', 'sent max', 'sent min', 'sent total', year_string, num_docs_string])
        for keyword in key_list:
            # populate each line with each sentiment calculation
            csvwriter.writerow([keyword, list_to_string(common.build_graph_list(keyword, year_list, sent_avg)),
                                list_to_string(common.build_graph_list(keyword, year_list, sent_max)),
                                list_to_string(common.build_graph_list(keyword, year_list, sent_min)),
                                list_to_string(common.build_graph_list(keyword, year_list, sent_total))])
        # write average sentiment across corpus in last line of csv file
        for keyword in overall_list:
            csvwriter.writerow([keyword, list_to_string(
                common.build_graph_list(keyword, year_list, overall_avg))])


if __name__ == '__main__':
    main()
