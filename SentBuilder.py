import json, os, shutil, argparse


#                                       *** SentBuilder.py ***
#
#   This script takes a corpus of Json document-formatted texts and a list of keywords / bigrams,
# and extracts a user-specified length of text around each occurrence of each keyword / bigram.
# It stores the results in subdirectories corresponding to each keyword / bigram.
#


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
                    title = jsondata["Title"]
                    author = jsondata["Author"]
                    year = int(jsondata["Year Published"])
                    text = jsondata[text_type]
                    for keyword in keywords:
                        if not bigrams:
                            # keep a set for more efficient word lookup,
                            # and a list to preserve ordering for file naming
                            word_set = set(keyword.split("/"))
                            words = keyword.split("/")
                            for i in range(len(text)):
                                if text[i] in word_set:
                                    word = text[i]
                                    sub_index += 1
                                    # build jsondoc out of text chunk around text[i]
                                    sub_text = text[(i - int(length/2)):(i + int(length/2))]
                                    with open(out_dir + "/" + "_".join(words) + "/" + str(index) + str(sub_index)
                                                      + '.json', 'w', encoding='utf-8') as out:
                                        out.write(build_json(title, author, word, year, sub_text))
                        else:
                            words = []
                            # build a list of tuples
                            for i in range(len(keyword)):
                                words.append("-".join(wd for wd in keyword[i]))
                            # for each tuple, search the text for occurrences of it
                            for i in range(len(keyword)):
                                for j in range(len(text) - 1):
                                    if text[j] == keyword[i][0] and text[j+1] == keyword[i][1]:
                                        sub_index += 1
                                        sub_text = text[(j - int(length/2)):(j + int(length/2))]
                                        # write extracted text to file
                                        with open(out_dir + "/" + "_".join(words) + "/" + str(index) + str(sub_index)
                                                          + '.json', 'w', encoding='utf-8') as out:
                                            word = " ".join(wd for wd in keyword[i])
                                            out.write(build_json(title, author, word, year, sub_text))


# json file to hold extracted text. in addition to extracted text, it also contains publication
# date (for sentiment analysis by period), title & author (to reference the book it came from)
# and the keyword itself, for reference.
def build_json(title, author, keyword, year, text):
    jfile = json.dumps({'Title': title, 'Author': author, 'Keyword': keyword, 'Year Published': year, 'Text': text},
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

    # make some variables global to simplify the function parameters
    global text_type, bigrams, length

    text_type = args.type
    bigrams = args.b
    length = int(args.len)

    # set up input directory and key list values
    in_dir = args.i
    out_dir = args.o
    keywords = build_key_list(args.k)

    # build subdirectories and populate them
    build_subdirs(out_dir, keywords)
    parse_json(in_dir, out_dir, keywords)

if __name__ == '__main__':
    main()
