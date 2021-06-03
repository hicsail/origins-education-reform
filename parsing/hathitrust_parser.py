import argparse, csv, os
from multiprocessing import Pool
import parsed
import parsing_help

def parse_csv(csv_file):
    htid_dict = {}
    with open(csv_file, 'r', encoding='utf-8') as csv_in:
        read_csv = csv.reader(csv_in, delimiter=',')
        for row in read_csv:
            # Skip header
            if row[0] == 'htid' or row[0] == "":
                continue

            htid_dict[row[0].strip()] = {
                "author": row[1].strip(), 
                "title": row[2].strip(),
                "year" :row[3].strip()
            }

    return htid_dict

def escape_htid(htid):
    htid = htid.replace(".", "_")
    htid = htid.replace("/", "=")
    htid = htid.replace(":", "+")
    return htid

def parse_files(filename):
    if filename.startswith("."):
        return

    # Load file
    obj = parsed.Parsed()

    with open(os.path.join(input_dir, filename), 'r', encoding='utf-8') as text:
        reading = False
        htid = None
        for line in text:
            if not reading and line.startswith("Find this book online:"):
                htid = line[51:].strip()
            elif line.startswith("##") and not reading:
                reading = True
            elif reading and not line.startswith("##"):
                parsing_help.add_content(line, obj, language)
    
    escaped_htid = escape_htid(htid)
    if htid not in htid_dict:
        raise Exception("Book " + htid + " not in CSV file!")

    obj.h = escaped_htid
    obj.a = htid_dict[htid]["author"]
    obj.t = htid_dict[htid]["title"]
    obj.y = htid_dict[htid]["year"]

    with open(os.path.join(output_dir, escaped_htid) + '.json', 'w') as out:
        out.write(parsing_help.build_json(obj))
        out.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help='Input directory with HathiTrust .txt files', action="store")
    parser.add_argument("output", help='Output directory for parsed .json files', action="store")
    parser.add_argument("csv", help='CSV file with text info', action="store")
    parser.add_argument("-lang", default="english", help='Corpus language', action="store")
    args = parser.parse_args()

    global input_dir, output_dir
    input_dir = os.path.normpath(args.input)
    output_dir = os.path.normpath(args.output)
    csv_file = os.path.normpath(args.csv)

    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    global language
    language = args.lang.lower()

    global htid_dict
    htid_dict = parse_csv(csv_file)

    filenames = []
    for _, _, files in os.walk(input_dir):
        for filename in files:
            filenames.append(filename)

    print("Parsing files")
    pool = Pool()
    pool.map_async(parse_files, filenames)
    pool.close()
    pool.join()