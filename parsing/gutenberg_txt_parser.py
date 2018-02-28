import csv, os, argparse, tqdm
from .. import parsing_help, parsed, common


def parse_link(src):
    splt = src.split("/")
    idno = splt[-2]
    return idno


def parse_csv(csv_in):
    ids = []
    with open(csv_in, 'r', encoding='utf-8') as csv_in:
        read_csv = csv.reader(csv_in, delimiter=',')
        for row in read_csv:
            if row[0] != 'source':
                src = row[0]
                idno = parse_link(src)
                ids.append((idno, row[1], row[2], row[3]))
    return ids


def get_idno(line):
    elems = line.split()
    elem = elems[-1]
    idno = elem[-5:-1]
    return idno


def match_pub_info(idno, ids):
    for tup in ids:
        if tup[0] == idno:
            return tup
    common.fail("Could not match idno for {0}".format(str(idno)))


def parse_txt(in_dir, ids, out_dir):
    for subdir, dirs, files in os.walk(in_dir):
        for txt_f in tqdm.tqdm(files):
            if txt_f[0] != ".":
                reading = False
                obj = parsed.Parsed()
                with open(in_dir + txt_f, 'r', encoding='utf-8') as txt_in:
                    for line in txt_in:
                        if 'Posting Date' in line:
                            idno = get_idno(line)
                            pub_info = match_pub_info(idno, ids)
                            obj.a, obj.t, obj.y = pub_info[1], pub_info[2], pub_info[3]
                        if 'START OF THIS PROJECT GUTENBERG EBOOK' in line:
                            reading = True
                        if 'END OF THIS PROJECT GUTENBERG EBOOK' in line:
                            reading = False
                        if reading and 'START OF THIS PROJECT GUTENBERG EBOOK' not in line:
                            parsing_help.add_content(line, obj, 'german')
                with open(out_dir + txt_f[:-4] + '.json', 'w', encoding='utf-8') as out:
                    out.write(parsing_help.build_json(obj))
                    out.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", metavar='in-directory', action="store", help="input directory argument")
    parser.add_argument("-o", help="output directory argument", action="store")
    parser.add_argument("-csv", help="csv file with publication dates", action="store")

    try:
        args = parser.parse_args()
    except IOError:
        common.fail("IOError")

    common.build_out(args.o)

    if args.csv is not None:
        ids = parse_csv(args.csv)
    else:
        common.fail("Please specify input csv file path")

    parse_txt(args.i, ids, args.o)

if __name__ == '__main__':
    main()