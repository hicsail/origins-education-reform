import json, os, shutil, argparse, tqdm
import common


# iterate through corpus, extract text surrounding occurrences of each
# keyword / bigram and write those to json files
def parse_json(in_dir, out_dir, keywords, by_sentences, length):
    # index and sub index for file naming
    index = 0
    sub_index = 0
    for subdir, dirs, files in os.walk(in_dir):
        print("Extracting snippets of text.")
        for jsondoc in tqdm.tqdm(files):
            if jsondoc[0] == ".":
                continue
            with open(in_dir + "/" + jsondoc, 'r', encoding='utf8') as in_file:
                index += 1
                jsondata = json.load(in_file)
                year = int(jsondata["Year"])
                if year < y_min or year >= y_max:
                    continue
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
                                        snippet = text[(i - length/2):(i + length/2)]
                                        for sentence in snippet:
                                            words_list.extend(sentence.split())
                                        sub_text = " ".join(snippet)
                                        write_to_file(out_dir, words, year, index, sub_index,
                                                      title, author, sub_text, words_list)
                            else:
                                if text[i] in word_set:
                                    sub_index += 1
                                    sub_words = text[(i - length/2):(i + length/2)]
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
                                                snippet = text[(j - length/2):(j + length/2)]
                                                for sent in snippet:
                                                    words_list.extend(sent.split())
                                                sub_text = " ".join(snippet)
                                                write_to_file(out_dir, words, year, index, sub_index,
                                                              title, author, sub_text, words_list)
                                else:
                                    if text[j] == keyword[i][0] and text[j+1] == keyword[i][1]:
                                        sub_index += 1
                                        sub_words = text[(j - length/2):(j + length/2)]
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
    jfile = json.dumps({'Title': title, 'Author': author, 'Keyword': keyword, 'Year': year, 'Text': text,
                        'Words': words},
                       sort_keys=True, indent=4, separators=(',', ': '), ensure_ascii=False)
    return jfile

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i",
        help="Input directory path",
        action="store",
        required=True
    )
    parser.add_argument(
        "-o",
        help="Output directory",
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
        "-len",
        type=int,
        help="Number of words around each keyword to keep",
        action="store",
        required=True
    )
    parser.add_argument(
        "-b",
        help="Set to analyze using bigrams",
        action="store_true"
    )
    parser.add_argument(
        "-type",
        help="Text field to use in analysis",
        default="Words",
        action="store",
        required=True
    )
    parser.add_argument(
        "-y",
        help="Start year and end year for grouping texts",
        action="store",
        required=True
    )
    parser.add_argument(
        "-sentences",
        help="Set to keep -len sentences around keywords instead of words",
        action="store_true"
    )

    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()

    # create / overwrite directory where results will be stored
    if not os.path.exists(args.o):
        os.mkdir(args.o)
    else:
        shutil.rmtree(args.o)
        os.mkdir(args.o)

    if args.sentences:
        print("Building snippets of {0} sentences around the specified keywords."
              .format(args.len))
    else:
        print("Building snippets of {0} words around the specified keywords."
              .format(args.len))

    # make some variables global to simplify the function parameters
    global text_type, bigrams, y_min, y_max

    type = args.type
    bigrams = args.b
    y_range = args.y.split()
    y_min = int(y_range[0])
    y_max = int(y_range[1])

    if args.sentences and "sentences" not in args.type.lower():
        raise Exception("Must use a Sentence field in -type with -sentences")
    elif not args.sentences "sentences" in args.type.lower():
        raise Exception("Cannot use a Sentence field in -type with -len")
    
    text_type = args.type
    keywords = common.build_key_list(args.k, args.b)

    # build subdirectories and populate them
    common.build_subdirs(args.o, keywords, args.b)
    parse_json(args.i, args.o, keywords, args.sentences, args.len)