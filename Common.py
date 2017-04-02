import tqdm, json, nltk, csv


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


# simplest dict with numbers as values, used for calculating word percentage
def buildSimpleDictOfNums(year_list):
    results = {}
    for year in year_list:
        results[year] = 0
    return results


# simplest dict with lists as values, used for calculating the top n words
def buildSimpleDictOfLists(year_list):
    results = {}
    for year in year_list:
        results[year] = []
    return results


# build a nested dict with lists as values
def buildDictOfLists(year_list, keywords):
    results = {}
    for year in year_list:
        for keyword in keywords:
            try:
                results[year][keyword] = []
            except KeyError:
                results[year] = {keyword: []}
    return results


# build a nested dict with individual numbers as values
def buildDictOfNums(year_list, keywords):
    results = {}
    for year in year_list:
        for keyword in keywords:
            try:
                results[year][keyword] = 0
            except KeyError:
                results[year] = {keyword: 0}
    return results


def fail(msg):
    print(msg)
    os._exit(1)
