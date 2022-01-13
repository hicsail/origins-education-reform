import json, csv, argparse, os, tqdm, nltk, operator
import common


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
            if jsondoc[0] == ".":
                continue
            with open(corpus + "/" + jsondoc, 'r', encoding='utf8') as in_file:
                jsondata = json.load(in_file)
                name = jsondoc

                year = jsondata["Year"]

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

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i",
        help="Input directory path",
        action="store",
        required=True
    )
    parser.add_argument(
        "-csv",
        help="CSV output filename",
        action="store",
        required=True
    )
    parser.add_argument(
        "-k",
        help="List of keywords for analysis",
        action="store",
        required=True
    )
    parser.add_argument(
        "-type",
        help="Text field to use in analysis",
        default="Words",
        action="store",
        required=True
    )
    parser.add_argument(
        "-bin",
        help="Set to analyze by texts instead of words",
        action="store_true"
    )

    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()

    keywords = args.k.lower().split("/")
    frequencies = take_frequencies(args.i, keywords, text_type, args.bin)

    with open(args.csv + '.csv', 'w', newline='', encoding='utf-8') as csv_out:
        csvwriter = csv.writer(csv_out, delimiter=',')
        row = ["filename", "publication date"]
        row.extend(keywords)
        if not args.bin:
            row.append("total words")
        csvwriter.writerow(row)
        sorted_freq = sorted(frequencies, key=operator.itemgetter(1))
        print("Writing to CSV\n")
        for volume in tqdm.tqdm(sorted_freq):
            csvwriter.writerow(volume)