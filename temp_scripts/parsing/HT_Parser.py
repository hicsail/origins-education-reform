import argparse, csv, os, shutil, zipfile
import xml.etree.ElementTree as ET
from nlp_scripts import parsed, common, parsing_help


def scan_for_htid(root):
    if "objectIdentifierValue" in root.tag:
        htid = root.text
        return htid
    else:
        for child in root:
            htid = scan_for_htid(child)
            if htid is not None:
                return htid


def build_htids(csvfile):
    htids = {}
    with open(csvfile, 'r', encoding='utf-8') as csv_in:
        read_csv = csv.reader(csv_in, delimiter=',')
        for row in read_csv:
            if row[0] != 'htid':
                try:
                    id = row[0].strip()
                    # author, title, year
                    htids[id] = [row[1], row[2], row[3]]
                except UnicodeDecodeError:
                    common.fail("Make sure the CSV files you are "
                                "referencing are UTF-8 encoded.")
    return htids


def test_file_htid(htids, folder, xml_file):
    # concatenate folder & file with f slash btwn (filepath to xml)
    xml = folder + "/" + xml_file
    tree = ET.parse(xml)
    root = tree.getroot()
    htid = scan_for_htid(root)
    htid = htid.replace("/", "=")
    htid= htid.replace(":", "+")
    if htid in htids:
        return [True, htid]
    else:
        return [False, htid]


def parse_files(in_dir, out_dir, htids, language):
    for folder, subfolders, files in os.walk(in_dir):
        if not subfolders:
            for xml_file in files:
                if xml_file[-4:] == ".xml":
                    htid_test = test_file_htid(htids, folder, xml_file)
                    # test if htid in set of htids, store it and build file if true
                    if htid_test[0]:
                        htid = htid_test[1]
                        obj = parsed.Parsed()
                        # replace periods for file-naming
                        obj.h = htid.replace(".", "_")
                        try:
                            obj.a = htids[htid][0]
                            obj.t = htids[htid][1]
                            obj.y = htids[htid][2]
                        except KeyError:
                            print("File with HTID {0} not found in CSV reference file.".format(htid))
                        for zip_file in files:
                            if zip_file[-4:] == ".zip":
                                with zipfile.ZipFile(folder + "/" + zip_file, 'r') as zf:
                                    for txt_file in zf.namelist():
                                        if txt_file[-4:] == ".txt":
                                            text = zf.read(txt_file).decode('utf-8')
                                            parsing_help.add_content(text, obj, language)
                            with open(out_dir + str(obj.h) + ".json", 'w', encoding='utf-8') as out:
                                out.write(parsing_help.build_json(obj))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-csv", help='path to CSV file', action="store")
    parser.add_argument("-o", help='output directory', action="store")
    parser.add_argument("-x", help='in-directory for HT files', action="store")
    parser.add_argument("-lang", help='language corpus is in', action="store")

    try:
        args = parser.parse_args()
    except IOError:
        pass

    if not os.path.exists(args.o):
        os.mkdir(args.o)
    else:
        shutil.rmtree(args.o)
        os.mkdir(args.o)

    language = args.lang.lower()
    htids = build_htids(args.csv)

    parse_files(args.x, args.o, htids, language)


if __name__ == '__main__':
    main()
