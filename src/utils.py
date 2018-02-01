import os
from nltk.stem.snowball import SnowballStemmer


def _fail(msg):
    """ Generic fail method for debugging. """

    print(msg)
    os._exit(1)


def num_dict(year_list, keywords=None, nested=0):
    """ Build empty dictionary with integers at leaf entries. """

    results = {}
    for year in year_list:
        if nested == 0:
            results[year] = 0
        elif nested == 1:
            results[year] = {}
            results[year]['TOTAL'] = 0
            for keyword in keywords:
                results[year][keyword] = 0
        else:
            _fail('Shouldn\'t be able to get here.')
    return results


def list_dict(year_list: list, keywords: [list, None]=None, nested: [None, int]=0):
    """ Build empty dictionary with lists at leaf entries. """

    results = {}
    for year in year_list:
        if nested == 0:
            results[year] = []
        elif nested == 1:
            results[year] = {}
            for keyword in keywords:
                results[year]['TOTAL'] = []
                results[year][keyword] = []
        else:
            _fail('Shouldn\'t be able to get here.')
    return results


def determine_year(year, year_list):
    """
    Given a year and list of year periods,
    return which period that year falls into.
    """

    for i in (range(len(year_list[:-1]))):
        if year_list[i] <= year < year_list[i + 1]:
            return year_list[i]
    _fail("{} is not in range".format(year))


def stem(word: str, language: [str, None] = 'english'):
    """
    Returns input word and its stem.
    """

    try:
        s = SnowballStemmer(language.lower())
    except ValueError:
        _fail("{} is not supported, please enter a valid language.".format(language))

    stemmed = s.stem(word.lower())

    return '{0}: {1}'.format(word, stemmed)


if __name__ == '__main__':

    print(stem('Runs', 'zorp'))








