import json, os, shutil, argparse, tqdm
import common


# iterate through corpus, extract text surrounding occurrences of each
# keyword / bigram and write those to json files
def parse_json(in_dir, out_dir, keywords, by_sentences):
    # index and sub index for file naming
    index = 0
    sub_index = 0
    for subdir, dirs, files in os.walk(in_dir):
        print("Extracting snippets of text.")
        for jsondoc in tqdm.tqdm(files):
            if jsondoc[0] != ".":
                with open(in_dir + "/" + jsondoc, 'r', encoding='utf8') as in_file:
                    index += 1
                    jsondata = json.load(in_file)
                    try:
                        year = int(jsondata["Year Published"])
                    except KeyError:
                        year = int(jsondata["Date"])
                    if y_min <= year <= y_max:
                        try:
                            title, author, text = jsondata["Title"], jsondata["Author"], jsondata[text_type[0]]
                        except KeyError:
                            title, author, text = jsondata["Title"], jsondata["Author"], jsondata[text_type[1]]
                        for keyword in keywords:
                            if not bigrams:
                                # keep a set for more efficient word lookup,
                                # and a list to preserve ordering for file naming
                                word_set = set(keyword.split("/"))
                                words = keyword.split("/")
                                for i in range(len(text)):
                                    if by_sentences:
                                        for word in text[i].split():
                                            if word in word_set:
                                                words_list = []
                                                sub_index += 1
                                                snippet = text[(i - int(length/2)):(i + int(length/2))]
                                                for sentence in snippet:
                                                    words_list.extend(sentence.split())
                                                sub_text = " ".join(snippet)
                                                write_to_file(out_dir, words, year, index, sub_index,
                                                              title, author, sub_text, words_list)
                                    else:
                                        if text[i] in word_set:
                                            sub_index += 1
                                            sub_words = text[(i - int(length/2)):(i + int(length/2))]
                                            sub_text = " ".join(sub_words)
                                            write_to_file(out_dir, words, year, index, sub_index,
                                                          title, author, sub_text, sub_words)
                            else:
                                words = []
                                # build a list of tuples
                                for i in range(len(keyword)):
                                    words.append("-".join(wd for wd in keyword[i]))
                                # for each tuple, search the text for occurrences of it
                                for i in range(len(keyword)):
                                    for j in range(len(text)):
                                        if by_sentences:
                                            sentence = text[j].split()
                                            if len(sentence) > 1:
                                                for k in range(len(sentence) - 1):
                                                    if sentence[k] == keyword[i][0] and sentence[k+1] == keyword[i][1]:
                                                        words_list = []
                                                        sub_index += 1
                                                        snippet = text[(j - int(length/2)):(j + int(length/2))]
                                                        for sent in snippet:
                                                            words_list.extend(sent.split())
                                                        sub_text = " ".join(snippet)
                                                        write_to_file(out_dir, words, year, index, sub_index,
                                                                      title, author, sub_text, words_list)
                                        else:
                                            if text[j] == keyword[i][0] and text[j+1] == keyword[i][1]:
                                                sub_index += 1
                                                sub_words = text[(j - int(length/2)):(j + int(length/2))]
                                                sub_text = " ".join(sub_words)
                                                write_to_file(out_dir, words, year, index, sub_index,
                                                              title, author, sub_text, sub_words)


def write_to_file(out_dir, words, year, index, sub_index, title, author, sub_text, sub_words):
    # write extracted text to file
    with open(out_dir + "/" + "_".join(words) + "/" + str(year) + "_"
                      + str(index) + "-" + str(sub_index)
                      + '.json', 'w', encoding='utf-8') as out:
        out.write(build_json(title, author, "_".join(words), year, sub_text,
                             sub_words))


# json file to hold extracted text. in addition to extracted text, it also contains publication
# date (for sentiment analysis by period), title & author (to reference the book it came from)
# and the keyword itself, for reference.
def build_json(title, author, keyword, year, text, words):
    jfile = json.dumps({'Title': title, 'Author': author, 'Keyword': keyword, 'Year Published': year, 'Text': text,
                        'Words': words},
                       sort_keys=True, indent=4, separators=(',', ': '), ensure_ascii=False)
    return jfile


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", metavar='in-dir', action="store", help="input directory argument")
    parser.add_argument("-o", metavar='out-dir', action="store", help="output directory argument")
    parser.add_argument("-k", action="store", help="list of keywords")
    parser.add_argument("-len", action="store", help="number of words to surround each keyword occurrence by")
    parser.add_argument("-b", help="boolean to control searching for bigrams rather than individual words",
                        action="store_true")
    parser.add_argument("-type", help="which text field from the json document you intend to analyze",
                        action="store")
    parser.add_argument("-y", help="year range", action="store")
    parser.add_argument("-sentences", help="extract number of sentences rather than words", action="store_true")

    try:
        args = parser.parse_args()
    except IOError:
        pass

    # create / overwrite directory where results will be stored
    if not os.path.exists(args.o):
        os.mkdir(args.o)
    else:
        shutil.rmtree(args.o)
        os.mkdir(args.o)

    if args.len is None:
        common.fail("Please specify snippet length.")

    if int(args.sentences) < 1:
        print("Building snippets of {0} words around the specified keywords."
              .format(args.len))
    else:
        print("Building snippets of {0} sentences around the specified keywords."
              .format(args.len))

    # make some variables global to simplify the function parameters
    global text_type, bigrams, length, y_min, y_max

    by_sentences = args.sentences
    type = args.type
    bigrams = args.b
    length = int(args.len)
    y_range = args.y.split()
    y_min = int(y_range[0])
    y_max = int(y_range[1])

    # determine which json field to parse based on input
    if by_sentences:
        if type.lower() == "full":
            text_type = "Full Sentences"
        elif type.lower() == "filtered":
            text_type = "Filtered Sentences"
        elif type.lower() == "stemmed":
            text_type = "Stemmed Sentences"
        elif type.lower() == "filtered stemmed":
            text_type = "Filtered Stemmed Sentences"
        else:
            text_type = type
    else:
        if type.lower() == "full":
            text_type = ["Full Text", "Text"]
        elif type.lower() == "filtered":
            text_type = ["Filtered Text", "Filtered"]
        elif type.lower() == "stemmed":
            text_type = ["Full Text Stemmed", "Stemmed"]
        elif type.lower() == "filtered stemmed":
            text_type = ["Filtered Text Stemmed", "Filtered Stemmed"]
        else:
            text_type = type

    # set up input directory and key list values
    in_dir = args.i
    out_dir = args.o
    keywords = common.build_key_list(args.k, bigrams)

    # build subdirectories and populate them
    common.build_subdirs(out_dir, keywords, bigrams)
    parse_json(in_dir, out_dir, keywords, by_sentences)

if __name__ == '__main__':
    main()
