import os


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


# construct list of year periods
def buildYearList(increment, range_years, periods, yrange_max, yrange_min):
    if not periods:
        num_elements = int(((yrange_max - yrange_min) / increment))
        year_list = [None] * num_elements
        i = 0
        for num in range(yrange_min, yrange_max, increment):
            year_list[i] = int(num)
            i += 1
    else:
        num_elements = len(range_years)
        year_list = [None] * num_elements
        i = 0
        for num in range_years:
            year_list[i] = int(num)
            i += 1
    return sorted(year_list)



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


# set up parameters for year range, depending on whether user is
# searching for fixed increments or specific periods of years
def year_params(range_years, periods):
    # if periods flag is not set, set up variables for fixed increments
    if not periods:
        yrange_min = int(range_years[0])
        increment = int(range_years[2])
        difference = int(range_years[1]) - yrange_min
        mod_val = difference % increment

        # adjust list of years so the end bit doesn't get cut out
        if mod_val != 0:
            yrange_max = int(range_years[1]) + (increment - mod_val) + increment
        else:
            yrange_max = int(range_years[1]) + increment
    # set up variables for periods rather than fixed increments
    else:
        yrange_min = int(range_years[0])
        yrange_max = int(range_years[len(range_years) - 1])
        increment = 0
    return[increment, yrange_min, yrange_max]


# helper method to group docs into periods
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


def fail(msg):
    print(msg)
    os._exit(1)
