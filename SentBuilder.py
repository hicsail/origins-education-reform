import json, os, shutil, argparse


# construct list of keywords
def build_key_list(keywords):
    key_list = keywords.lower().split(",")
    key_list = [keyword.strip() for keyword in key_list]
    if bigrams:
        bigram_list = []
        key_list = [tuple(keyword.split("/")) for keyword in key_list]
        # if a bigram is by itself, i.e. - not associated with other bigrams via "/",
        # then this loop will create a tuple with the second index empty. Keep an eye
        # on it with the word frequency methods, I don't know if it will cause a
        # problem yet.
        for i in range(len(key_list)):
            temp_list = list(key_list[i])
            temp_list = [tuple(elem.split()) for elem in temp_list]
            temp_list = tuple(temp_list)
            bigram_list.append(temp_list)
        return bigram_list
    return key_list


# build subdirectories within output directory, each containing
# documents where a single keyword / bigram occurs
def build_subdirs(out_dir, keywords):
    for keyword in keywords:
        if not bigrams:
            words = keyword.split("/")
            dir_name = "_".join(words)
            os.mkdir(out_dir + "/" + dir_name)
        else:
            words = []
            for i in range(len(keyword)):
                words.append("-".join(wd for wd in keyword[i]))
            dir_name = "_".join(words)
            os.mkdir(out_dir + "/" + dir_name)


# iterate through corpus, extract text surrounding occurrences of each
# keyword / bigram and write those to json files
def parse_json(in_dir, out_dir, keywords):
    # index and sub index for file naming
    index = 0
    sub_index = 0
    for subdir, dirs, files in os.walk(in_dir):
        for jsondoc in files:
            if jsondoc[0] != ".":
                with open(in_dir + "/" + jsondoc, 'r', encoding='utf8') as in_file:
                    index += 1
                    jsondata = json.load(in_file)
                    year = int(jsondata["Year Published"])
                    if y_min <= year <= y_max:
                        title = jsondata["Title"]
                        author = jsondata["Author"]
                        text = jsondata[text_type]
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
                                                # build jsondoc out of text chunk around word
                                                with open(out_dir + "/" + "_".join(words) + "/" + str(year) + "_"
                                                                  + str(index) + "-" + str(sub_index)
                                                                  + '.json', 'w', encoding='utf-8') as out:
                                                    out.write(build_json(title, author, "_".join(words), year, sub_text,
                                                                         words_list))
                                    if by_words:
                                        if text[i] in word_set:
                                            sub_index += 1
                                            sub_words = text[(i - int(length/2)):(i + int(length/2))]
                                            sub_text = " ".join(sub_words)
                                            # build jsondoc out of text chunk around word
                                            with open(out_dir + "/" + "_".join(words) + "/" + str(year) + "_"
                                                              + str(index) + "-" + str(sub_index)
                                                              + '.json', 'w', encoding='utf-8') as out:
                                                out.write(build_json(title, author, "_".join(words), year, sub_text,
                                                                     sub_words))
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
                                                        # write extracted text to file
                                                        with open(out_dir + "/" + "_".join(words) + "/" + str(year)
                                                                          + "_" + str(index) + "-" + str(sub_index)
                                                                          + '.json', 'w', encoding='utf-8') as out:
                                                            out.write(build_json(title, author, "_".join(words), year,
                                                                                 sub_text, words_list))
                                        if by_words:
                                            if text[j] == keyword[i][0] and text[j+1] == keyword[i][1]:
                                                sub_index += 1
                                                sub_words = text[(j - int(length/2)):(j + int(length/2))]
                                                sub_text = " ".join(sub_words)
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
    parser.add_argument("-words", help="extract number of words rather than sentences", action="store_true")
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

    def fail(msg):
        print(msg)
        os._exit(1)

    if int(args.words) + int(args.sentences) < 1:
        msg = "Please select either -words or -sentences."
        fail(msg)

    if int(args.words) + int(args.sentences) > 1:
        msg = "Please select either -words or -sentences, not both."
        fail(msg)

    # make some variables global to simplify the function parameters
    global text_type, bigrams, length, y_min, y_max, by_words, by_sentences

    by_words = args.words
    by_sentences = args.sentences
    type = args.type
    bigrams = args.b
    length = int(args.len)
    y_range = args.y.split()
    y_min = int(y_range[0])
    y_max = int(y_range[1])

    # determine which json field to parse based on input
    if by_words:
        if type == "Full":
            text_type = "Full Text"
        if type == "Filtered":
            text_type = "Filtered Text"
        if type == "Stemmed":
            text_type = "Full Text Stemmed"
        if type == "Filtered Stemmed":
            text_type = "Filtered Text Stemmed"
    if by_sentences:
        if type == "Full":
            text_type = "Full Sentences"
        if type == "Filtered":
            text_type = "Filtered Sentences"
        if type == "Stemmed":
            text_type = "Stemmed Sentences"
        if type == "Filtered Stemmed":
            text_type = "Filtered Stemmed Sentences"

    # set up input directory and key list values
    in_dir = args.i
    out_dir = args.o
    keywords = build_key_list(args.k)

    # build subdirectories and populate them
    build_subdirs(out_dir, keywords)
    parse_json(in_dir, out_dir, keywords)

if __name__ == '__main__':
    main()
