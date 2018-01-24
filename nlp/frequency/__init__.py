import json, tqdm
from nlp.utils import *


def word_frequency(in_dir, text_type, year_list, key_list):
    """
    Calculates word frequencies across a corpus, given an input
    directory, list of years and keywords.

    :param in_dir: input path to corpus
    :param text_type: name of text field in corpus json files
    :param year_list: list of years, e.g. [year-1, year-2, ... , year-n]
    :param key_list: keyword list, keywords that shoudl be grouped together
    should be separated by a forward slash, e.g. ['key1', 'key2/key3', 'key4']
    :return:
    """

    n = detect_n(key_list)
    key_list = build_key_list(key_list)

    word_totals = num_dict(year_list)
    keyword_counts = num_dict(year_list, key_list, 1)
    frequency_lists = list_dict(year_list, key_list, 1)

    for subdir, dirs, files in os.walk(in_dir):
        print("Taking word counts")
        for jsondoc in tqdm.tqdm(files):
            if jsondoc[0] != ".":
                with open(in_dir + "/" + jsondoc, 'r', encoding='utf8') as in_file:
                    jsondata = json.load(in_file)


    return


def detect_n(keys: str):
    """
    Detect value of n for word frequency.

    :param keys: string of keywords or n-grams, separated
    by a forward slash if there are more than one '/'
    :return: integer
    """
    keys = keys.split('/')

    lengths = set()
    for k in keys:
        lengths.add(len(k.split()))

    assert(len(lengths) == 1)

    return lengths.pop()


if __name__ == '__main__':

    a = 'a a/b '
    print(detect_n(a))

'''
# build list of keywords, supports individual keywords or bigrams
def build_key_list(keywords, bigrams):
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

'''