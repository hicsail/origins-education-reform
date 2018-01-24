import os


# generic fail method
def fail(msg):
    print(msg)
    os._exit(1)


def num_dict(year_list, keywords=None, nested=0):
    results = {}
    for year in year_list:
        if nested == 0:
            results[year] = 0
        elif nested == 1:
            for keyword in keywords:
                results[year][keyword] = 0
        elif nested == 2:
            results[year] = {}
            for keyword in keywords:
                results[year][keyword] = {}
                results[year][keyword]["TOTAL"] = 0
                for k in keyword.split("/"):
                    results[year][keyword][k] = 0
        else:
            fail('Shouldn\'t be able to get here.')
    return results


def list_dict(year_list, keywords=None, nested=0):
    results = {}
    for year in year_list:
        if nested == 0:
            results[year] = []
        elif nested == 1:
            for keyword in keywords:
                results[year][keyword] = []
        else:
            fail('Shouldn\'t be able to get here.')
    return results


def build_key_list(keys):

    return [tuple(k.split()) for k in keys.split('/')]


if __name__ == '__main__':
    a = build_key_list('the/the')
    print(a)

