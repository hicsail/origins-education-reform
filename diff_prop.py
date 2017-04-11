import common, csv, argparse, tqdm
import statsmodels.api
import scipy.stats


def build_samples(csv_inpt, year_list, yrange_min, yrange_max):
    # set up observation and sample size dicts
    p = common.buildSimpleDictOfNums(year_list)
    n = common.buildSimpleDictOfNums(year_list)
    with open(csv_inpt, 'r') as csv_file:
        read_csv = csv.reader(csv_file, delimiter=',')
        row1 = next(read_csv)
        # this column is populated if the csv file stores word frequencies
        if row1[-1] == "total words":
            binary = False
        else:
            binary = True
        print("Building a set of samples")
        for row in tqdm.tqdm(read_csv):
            if row[0] != "filename":
                year = int(row[1])
                # check to make sure it's within range specified by user
                if yrange_min <= year < yrange_max:
                    # determine which period it falls within
                    target = common.determine_year(year, year_list)
                    try:
                        if binary:
                            # one more volume to sample size w/r/t year period
                            n[target] += 1
                        else:
                            # add total words to sample size w/r/t year period
                            n[target] += int(row[-1])
                    except KeyError:
                        pass
                    for cell in row[2:-1]:
                        if binary:
                            if cell == "1":
                                try:
                                    # add one to observation dict and break
                                    p[target] += 1
                                    break
                                except KeyError:
                                    pass
                        else:
                            try:
                                # add frequency in this cell to observation dict
                                p[target] += int(cell)
                            except KeyError:
                                pass
    return [p, n]


def diff_props_test(k1, n1, k2, n2):
    # Documentation:
    # http://statsmodels.sourceforge.net/devel/generated/statsmodels.stats.proportion.proportions_ztest.html

    # Example:
    # http://knowledgetack.com/python/statsmodels/proportions_ztest/

    (z, p_value) = statsmodels.api.stats.proportions_ztest([k1, k2], [n1, n2], alternative='two-sided', prop_var=False)
    return [z, p_value]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-csv", help="input csv files argument", action="store")
    parser.add_argument("-txt", help="output text filepath", action="store")
    parser.add_argument("-y", help="min/max for year range and increment value, surround with quotes",
                        action="store")
    parser.add_argument("-p", help="boolean to analyze by different periods rather than a fixed increment value",
                        action="store_true")

    try:
        args = parser.parse_args()
    except IOError as msg:
        common.fail(msg)

    if args.csv is None or len(args.csv.split()) != 2:
        common.fail("Please enter two csv files after -csv, separated by whitespace.")
    else:
        csv_files = args.csv.split()

    if args.txt is None:
        common.fail("Please enter output text file path.")

    periods = args.p

    range_years = args.y.split()
    year_params = common.year_params(range_years, periods)
    increment, yrange_min, yrange_max = year_params[0], year_params[1], year_params[2]

    year_list = common.buildYearList(increment, range_years, periods, yrange_max, yrange_min)

    first = build_samples(csv_files[0], year_list, yrange_min, yrange_max)
    x1 = first[0]
    n1 = first[1]
    second = build_samples(csv_files[1], year_list, yrange_min, yrange_max)
    x2 = second[0]
    n2 = second[1]

    diff_props = []
    critical = scipy.stats.norm.ppf(1-(0.05/2))

    # calculate chi-squared and p values
    for year in tqdm.tqdm(year_list):
        vals = diff_props_test(x1[year], n1[year], x2[year], n2[year])
        z = vals[0]
        p_val = vals[1]
        significance = scipy.stats.norm.cdf(z)
        diff_props.append((z, p_val, significance))

    with open(args.txt + '.txt', 'w') as txt_out:
        for i in range(len(diff_props) - 1):
            txt_out.write("Period: {0} - {1}".format(str(year_list[i]), str(year_list[i+1])) + "\n")
            txt_out.write("Z-score: " + str(diff_props[i][0]) + "\n")
            txt_out.write("P value: " + str(diff_props[i][1]) + "\n")
            txt_out.write("Significance: " + str(diff_props[i][2]) + "\n")
            txt_out.write("Critical: " + str(critical) + "\n\n")

if __name__ == '__main__':
    main()
