import json, csv, argparse, Common, os, tqdm, nltk, operator


# take either 0/1 occurrence values on snippets or word frequencies
# on fulltext files, method depends on value of text_type
def take_frequencies(corpus, keywords, text_type, binary):
    for subdir, dirs, files in os.walk(corpus):
        frequencies = []
        if text_type == 'Words':
            print("Building Occurrence Tables\n")
        else:
            print("Building Frequency Tables\n")
        for jsondoc in tqdm.tqdm(files):
            if jsondoc[0] != ".":
                with open(corpus + "/" + jsondoc, 'r', encoding='utf8') as in_file:
                    jsondata = json.load(in_file)
                    name = jsondoc
                    year = jsondata["Year Published"]
                    row = [name, year]
                    # take 0/1 occurrences on snippet files
                    if binary:
                        text = set(jsondata[text_type])
                        for keyword in keywords:
                            if keyword in text:
                                row.append("1")
                            else:
                                row.append("0")
                        frequencies.append(row)
                    # take keyword frequencies on fulltext files
                    else:
                        text = set(jsondata[text_type])
                        length = len(jsondata[text_type])
                        fulltext = jsondata[text_type]
                        fdist = nltk.FreqDist(fulltext)
                        for keyword in keywords:
                            if keyword in text:
                                row.append(str(fdist[keyword]))
                            else:
                                row.append("0")
                        row.append(length)
                        frequencies.append(row)
        return frequencies


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", metavar='in-directory', action="store", help="input directory argument")
    parser.add_argument("-csv", help="output csv file argument", action="store")
    parser.add_argument("-k", help="list of keywords argument, surround list with quotes", action="store")
    parser.add_argument("-type", help="set the name of the text field you're analyzing", action="store")
    parser.add_argument("-bin", help="track binary (0/1) occurrence, default is raw frequency", action="store_true")


    try:
        args = parser.parse_args()
    except IOError as msg:
        Common.fail(parser.error(str(msg)))

    if args.i is None:
        Common.fail("Please specify input directory.")
    else:
        corpus = args.i

    binary = args.bin
    keywords = args.k.lower().split("/")

    if args.type is not None:
        if args.type.lower() == "full":
            text_type = "Full Text"
        elif args.type.lower() == "filtered":
            text_type = "Filtered Text"
        elif args.type.lower() == "stemmed":
            text_type = "Full Text Stemmed"
        elif args.type.lower() == "filtered stemmed":
            text_type = "Filtered Text Stemmed"
        else:
            text_type = args.type
    else:
        text_type = "Words"

    frequencies = take_frequencies(corpus, keywords, text_type, binary)

    with open(args.csv + '.csv', 'w', newline='', encoding='utf-8') as csv_out:
        csvwriter = csv.writer(csv_out, delimiter=',')
        row = ["filename", "publication date"]
        row.extend(keywords)
        if not binary:
            row.append("total words")
        csvwriter.writerow(row)
        sorted_freq = sorted(frequencies, key=operator.itemgetter(1))
        print("Writing to CSV\n")
        for volume in tqdm.tqdm(sorted_freq):
            csvwriter.writerow(volume)

if __name__ == '__main__':
    main()
