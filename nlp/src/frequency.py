"""

want to be able to call Frequency() on a corpus, key_list, and year range to get a json object
back with the relevant breakdowns
"""
import json


class Frequency:
    def __init__(self, i):
        with open(i, 'r', encoding='utf8') as jc:
            cfg = json.load(jc)
            self.corpus_path = cfg['Paths']['Path to corpus']
            self.text_path = cfg['Paths']['Output text file path']
            self.json_path = cfg['Paths']['Output json file path']

            self.bigrams = cfg['Booleans']['Bigrams']
            self.periods = cfg['Booleans']['Periods']

            self.key_list = self._build_key_list(cfg['Parameters']['Keywords'])
            self.year_list = cfg['Parameters']['Year list']
            self.num = cfg['Parameters']['Top words [num]']
            self.type = cfg['Parameters']['Type']

    def _build_key_list(self, keys):
        key_list = keys.lower().split(",")
        key_list = [keyword.strip() for keyword in key_list]
        if self.bigrams:
            bigram_list = []
            key_list = [tuple(keyword.split("/")) for keyword in key_list]
            for i in range(len(key_list)):
                temp_list = list(key_list[i])
                temp_list = [tuple(elem.split()) for elem in temp_list]
                temp_list = tuple(temp_list)
                bigram_list.append(temp_list)
            return bigram_list
        return key_list




"""
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
"""