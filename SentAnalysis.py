import os, argparse, json, csv


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


# construct list of year periods
def build_year_list(increment, range_years):
    if not periods:
        # fixed increments
        num_elements = int(((yrange_max - yrange_min) / increment))
        year_list = [None] * num_elements
        i = 0
        for num in range(yrange_min, yrange_max, increment):
            year_list[i] = num
            i += 1
    else:
        # periods of arbitrary length
        num_elements = len(range_years)
        year_list = [None] * num_elements
        i = 0
        for num in range_years:
            year_list[i] = int(num)
            i += 1
    return sorted(year_list)


# build a 2D dict with lists as values
def build_dict_of_lists(year_list, keywords):
    results = {}
    for year in year_list:
        for keyword in keywords:
            try:
                results[year][keyword] = []
            except KeyError:
                results[year] = {keyword: []}
    return results


# build a 2D dict with individual numbers as values
def build_dict_of_nums(year_list, keywords):
    results = {}
    for year in year_list:
        for keyword in keywords:
            try:
                results[year][keyword] = 0
            except KeyError:
                results[year] = {keyword: 0}
    return results


# build dict of words corresponding to the AFINN word list and their pos/neg values
def build_afinn_dict(filepath):
    afinn = {}
    with open(filepath, 'r', encoding='utf-8') as in_file:
        lines = [line.rstrip('\n') for line in in_file]
        for ws in lines:
            line = ws.split()
            try:
                wd = line[0].strip()
                sent = (line[1].strip())
                sent = int(sent)
                afinn[wd] = sent
            except ValueError:
                pass
    return afinn


# helper method to group json docs into periods
def determine_year(year, year_list):
    # determine which period it falls within
    for i in range(len(year_list)):
        if year_list[i] <= year < year_list[i + 1]:
            # the year / period this document belongs in
            target = year_list[i]
            return target
        if year >= year_list[len(year_list) - 1]:
            # case when the document belongs in the last year / period of the list
            target = year_list[len(year_list) - 1]
            return target
        else:
            continue


# sort dict entries in a list of tuples by second value (i.e. - sentiment score)
def sort_sent_dict(year_list, key_list, sent_results):
    for year in year_list:
        for keyword in key_list:
            sent_results[year][keyword] = sorted(sent_results[year][keyword], key=lambda x: x[1])
    return sent_results


# build dict needed to calculate average sentiment across corpus, per N words
def populate_overall_sentiment(directory, overall_list, year_list, afinn, extract_length):
    overall_sent = build_dict_of_lists(year_list, overall_list)
    for subdir, dirs, files in os.walk(directory):
        for jsondoc in files:
            if jsondoc[0] != ".":
                with open(directory + "/" + jsondoc, 'r', encoding='utf8') as inpt:
                    sentiment = 0
                    jsondata = json.load(inpt)
                    text = jsondata["Full Text"]
                    truncated = float(len(text)/extract_length)
                    year = int(jsondata["Year Published"])
                    # check to make sure it's within range specified by user
                    if yrange_min <= year < yrange_max:
                        # determine which period it falls within
                        target = determine_year(year, year_list)
                        for word in text:
                            if word in afinn:
                                sentiment += afinn[word]
                        # even though overall_list only has one keyword, this looks
                        # better than just hard-coding "all" within the method
                        truncated_sentiment = float(sentiment/truncated)
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
                    if jsondoc[0] != ".":
                        with open(dirs + "/" + subdir + "/" + jsondoc, 'r', encoding='utf8') as inpt:
                            jsondata = json.load(inpt)
                            text = jsondata["Text"]
                            length = len(text)
                            return length


# fill sent dict with sent results for each json doc w/r/t AFINN dict
def populate_sent_dict(directory, key_list, year_list, afinn):
    sent_dict = build_dict_of_lists(year_list, key_list)
    for dirs, subdirs, files in os.walk(directory):
        for subdir in subdirs:
            for folders, subfolders, file in os.walk(dirs + "/" + subdir):
                for jsondoc in file:
                    if jsondoc[0] != ".":
                        with open(dirs + "/" + subdir + "/" + jsondoc, 'r', encoding='utf8') as inpt:
                            sentiment = 0
                            jsondata = json.load(inpt)
                            text = jsondata["Text"]
                            year = int(jsondata["Year Published"])
                            # check to make sure it's within range specified by user
                            if yrange_min <= year < yrange_max:
                                target = determine_year(year, year_list)
                                for word in text:
                                    if word in afinn:
                                        sentiment += afinn[word]
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
    sent_result = build_dict_of_nums(year_list, key_list)
    for i in range(len(year_list)):
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
                if length > 0 or total > 0:
                    try:
                        average = round((total / length), 4)
                        sent_result[year_list[i]][keyword] = average
                    except ZeroDivisionError:
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


# writes N=num documents with highest sentiment scores for each period to a text file
def list_max_docs(out, year, keyword, results, num):
    list_length = len(results[year][keyword])
    if int(num) <= list_length:
        # make sure user requested less tf-idf scores than actually exist for that period
        out.write("{0} highest sentiment scores for \"{1}\" in this period: ".format(str(num), str(keyword)) + "\n")
        i = 1
        for key_tup in results[year][keyword][list_length - int(num): list_length]:
            out.write("{0}. {1}: {2}".format(str(i), str(key_tup[0]), str(key_tup[1])) + "\n")
            i += 1
        out.write("\n")
    else:
        # user requested more tf-idf scores than there are for that period
        out.write("{0} highest sentiment scores for \"{1}\" in this period: ".format(str(list_length), str(keyword)) + "\n")
        i = 1
        for key_tup in results[year][keyword]:
            out.write("{0}. {1}: {2}".format(str(i), str(key_tup[0]), str(key_tup[1])) + "\n")
            i += 1
        out.write("\n")


# writes N=num documents with lowest sentiment scores for each period to a text file
def list_min_docs(out, year, keyword, results, num):
    list_length = len(results[year][keyword])
    if int(num) <= list_length:
        # make sure user requested less tf-idf scores than actually exist for that period
        out.write("{0} lowest sentiment scores for \"{1}\" in this period: ".format(str(num), str(keyword)) + "\n")
        i = 1
        for key_tup in results[year][keyword][:int(num)]:
            out.write("{0}. {1}: {2}".format(str(i), str(key_tup[0]), str(key_tup[1])) + "\n")
            i += 1
        out.write("\n")
    else:
        # user requested more tf-idf scores than there are for that period
        out.write("{0} lowest sentiment scores for \"{1}\" in this period: ".format(str(list_length), str(keyword)) + "\n")
        i = 1
        for key_tup in results[year][keyword]:
            out.write("{0}. {1}: {2}".format(str(i), str(key_tup[0]), str(key_tup[1])) + "\n")
            i += 1
        out.write("\n")


# can't store lists in csv file, so need to store data in string
def list_to_string(list_inpt):
    return_string = ""
    for wd in list_inpt:
        return_string += (str(wd) + " ")
    return return_string


# returns a list of values to be plotted
def build_graph_list(keyword, year_list, param):
    a = [0] * len(year_list)
    for i in range(len(year_list)):
        a[i] += param[year_list[i]][keyword]
    return a


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", metavar='in-dir', action="store", help="input directory argument")
    parser.add_argument("-c", help="file path to full corpus", action="store")
    parser.add_argument("-afinn", help="file path to AFINN word list", action="store")
    parser.add_argument("-y", help="min/max for year range and increment value, surround with quotes",
                        action="store")
    parser.add_argument("-num", help="number of max/min documents to grab from each period", action="store")
    parser.add_argument("-p", help="boolean to analyze by different periods rather than a fixed increment value",
                        action="store_true")
    parser.add_argument("-csv", help="file path to csv output", action="store")
    parser.add_argument("-txt", help="file path to txt output", action="store")

    try:
        args = parser.parse_args()
    except IOError:
        pass

    global periods, yrange_min, yrange_max

    periods = args.p
    directory = args.i
    corpus_path = args.c

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
        # how many samples between each year range
        year_list = build_year_list(increment, range_years)

    # set up variables for periods rather than fixed increments
    else:
        range_years = args.y.split()
        yrange_min = int(range_years[0])
        yrange_max = int(range_years[len(range_years) - 1])
        increment = 0

        # initialize list of years and dict to keep track of
        # how many samples in each period
        year_list = build_year_list(increment, range_years)

    # set up dicts for sentiment word list, keyword list, & results of sentiment analysis
    afinn = build_afinn_dict(args.afinn)
    key_list = build_key_list(directory)
    extract_len = determine_text_length(directory)
    overall_list = ["Average Sentiment Across Corpus"]

    # master dict with raw sent scores and their corresponding json doc file names
    sent_results = populate_sent_dict(directory, key_list, year_list, afinn)
    overall_sent = populate_overall_sentiment(corpus_path, overall_list, year_list, afinn, extract_len)

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
                    list_max_docs(txt_out, year_list[i], keyword, sent_results, args.num)
                    list_min_docs(txt_out, year_list[i], keyword, sent_results, args.num)
                except (AttributeError, UnboundLocalError, TypeError) as e:
                    # user didn't want max/min n words
                    pass
            txt_out.write("\n")

    # create a csv file and write sentiment scores to it
    with open(args.csv + '.csv', 'w', newline='', encoding='utf-8') as csv_out:
        csvwriter = csv.writer(csv_out, delimiter=',')
        year_list_str = []
        for year in year_list:
            year_list_str.append(str(year))
        year_string = " ".join(year_list_str)
        csvwriter.writerow(['word', 'sent avg', 'sent max', 'sent min', 'sent total', year_string])
        for keyword in key_list:
            # populate each line with each sentiment calculation
            csvwriter.writerow([keyword, list_to_string(build_graph_list(keyword, year_list, sent_avg)),
                                list_to_string(build_graph_list(keyword, year_list, sent_max)),
                                list_to_string(build_graph_list(keyword, year_list, sent_min)),
                                list_to_string(build_graph_list(keyword, year_list, sent_total))])
        # write average sentiment across corpus in last line of csv file
        for keyword in overall_list:
            csvwriter.writerow([keyword, list_to_string(build_graph_list(keyword, year_list, overall_avg))])

if __name__ == '__main__':
    main()
