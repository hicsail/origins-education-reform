import os, tqdm, math, shutil


# generic fail method
def fail(msg):
    print(msg)
    os._exit(1)


def build_out(out_dir):
    if out_dir is not None:
        # create / overwrite directory where results will be stored
        if not os.path.exists(out_dir):
            os.mkdir(out_dir)
        else:
            shutil.rmtree(out_dir)
            os.mkdir(out_dir)
    else:
        fail("Please specify output directory.")


# build subdirectories within output directory, each containing
# documents where a single keyword / bigram occurs
def build_subdirs(out_dir, keywords, bigrams):
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


# construct list of year periods
def build_year_list(increment, range_years, periods, yrange_max, yrange_min):
    if not periods:
        num_elements = int(((yrange_max - yrange_min) / increment))
        year_list = [None] * num_elements
        i = 0
        for num in range(yrange_min, yrange_max, increment):
            year_list[i] = num
            i += 1
    else:
        num_elements = len(range_years)
        year_list = [None] * num_elements
        i = 0
        for num in range_years:
            year_list[i] = int(num)
            i += 1
    return sorted(year_list)


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


# simplest dict with numbers as entries
def build_simple_dict_of_nums(year_list):
    results = {}
    for year in year_list:
        results[year] = 0
    return results


# simplest dict with lists as entries
def build_simple_dict_of_lists(year_list):
    results = {}
    for year in year_list:
        results[year] = []
    return results


# build a nested dict with lists as leaf entries
def build_dict_of_lists(year_list, keywords):
    results = {}
    for year in year_list:
        for keyword in keywords:
            try:
                results[year][keyword] = []
            except KeyError:
                results[year] = {keyword: []}
    return results


# build a nested dict with numbers as leaf entries
def build_dict_of_nums(year_list, keywords):
    results = {}
    for year in year_list:
        for keyword in keywords:
            try:
                results[year][keyword] = 0
            except KeyError:
                results[year] = {keyword: 0}
    return results


# build a nested dict with dicts as leaf entries
def build_dict_of_dicts(year_list, key_list):
    results = {}
    for year in year_list:
        for key in key_list:
            try:
                results[year][key] = {}
            except KeyError:
                results[year] = {key: {}}
    return results


# returns a list of values to be plotted
def build_graph_list(keyword, year_list, param):
    a = [0] * len(year_list)
    for i in range(len(year_list)):
        a[i] += param[year_list[i]][keyword]
    return a


# can't store lists in csv file, so need to store data in string
def list_to_string(list_inpt):
    return_string = ""
    for wd in list_inpt:
        return_string += (str(wd) + " ")
    return return_string


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


# writes N documents with lowest scores for each period to a text file
def list_min_docs(out, year, keyword, results, num, analysis):
    list_length = len(results[year][keyword])
    if int(num) <= list_length:
        # user requested less scores than exist for that period
        out.write("{0} lowest {1} scores for \"{2}\" in this period: "
                  .format(str(num), analysis, str(keyword)) + "\n")
        i = 1
        for key_tup in results[year][keyword][:int(num)]:
            out.write("{0}. {1}: {2}".format(str(i), str(key_tup[0]), str(key_tup[1])) + "\n")
            i += 1
        out.write("\n")
    else:
        # user requested more scores than exist for that period
        out.write("{0} lowest {1} scores for \"{1}\" in this period: "
                  .format(str(list_length), analysis, str(keyword)) + "\n")
        i = 1
        for key_tup in results[year][keyword]:
            out.write("{0}. {1}: {2}".format(str(i), str(key_tup[0]), str(key_tup[1])) + "\n")
            i += 1
        out.write("\n")


# writes N documents with highest scores for each period to a text file
def list_max_docs(out, year, keyword, results, num, analysis):
    list_length = len(results[year][keyword])
    if int(num) <= list_length:
        out.write("{0} highest {1} scores for \"{2}\" in this period: "
                  .format(str(num), analysis, str(keyword)) + "\n")
        i = 1
        for key_tup in results[year][keyword][list_length - int(num): list_length]:
            out.write("{0}. {1}: {2}".format(str(i), str(key_tup[0]), str(key_tup[1])) + "\n")
            i += 1
    else:
        out.write("{0} highest {1} scores for \"{2}\" in this period: "
                  .format(str(list_length), analysis, str(keyword)) + "\n")
        i = 1
        for key_tup in results[year][keyword]:
            out.write("{0}. {1}: {2}".format(str(i), str(key_tup[0]), str(key_tup[1])) + "\n")
            i += 1


# keeping the following two methods just in case we come back to them
def build_z_list(year_list, x1, x2, n1, n2):
    z = []
    for year in tqdm.tqdm(year_list):
        z.append(z_test(x1[year], n1[year], x2[year], n2[year]))
    return z


def z_test(x1, n1, x2, n2):
    p1 = x1/n1
    p2 = x2/n2

    p = float((p1*n1 + p2*n2)/(n1 + n2))
    se = (p*(1-p))*((n1 + n2)/(n1*n2))
    se = math.sqrt(se)

    z = (p1 - p2)/se

    return z
