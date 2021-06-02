import argparse, csv, os, xlrd

def load_sheets():
    wb = xlrd.open_workbook(input_path)

    return wb.sheets()

def filter_row(vals):
    ret = []

    for s in vals:
        if isinstance(s, str):
            ret.append(s.replace(",", ""))
        elif isinstance(s, float):
            ret.append(int(s))
        else:
            ret.append(s)

    return ret

def convert_and_write():
    sheets = load_sheets()

    for s in sheets:

        with open("{0}/{1}.csv".format(output_path, s.name), 'w') as f:
            wr = csv.writer(f, quoting=csv.QUOTE_ALL)

            for j in range(s.nrows):
                wr.writerow(filter_row(s.row_values(j)[:7]))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help='Input Excel file', action="store")
    parser.add_argument("output", help='Output directory for CSV files', action="store")
    args = parser.parse_args()

    global input_path, output_path
    input_path = os.path.normpath(args.input)
    output_path = os.path.normpath(args.output)

    convert_and_write()