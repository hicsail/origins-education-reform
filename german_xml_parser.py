import argparse, os, parsing_help, parsed, common, csv, json
import xml.etree.ElementTree as ET


def get_text(root, file):
    for child in root:
        if 'div' in child.tag:
            for children in child:
                if 'div' in children.tag:
                    for more_children in children:
                        if more_children.tag == "{http://www.tei-c.org/ns/1.0}p" or \
                                more_children.tag == "{http://www.tei-c.org/ns/1.0}lg" or \
                                more_children.tag == "{http://www.tei-c.org/ns/1.0}head":
                            parsing_help.add_xml_content(more_children, file, 'german')
                            for even_more_children in more_children:
                                parsing_help.add_xml_content(even_more_children, file, 'german')
                                for wow_more_children in even_more_children:
                                    parsing_help.add_xml_content(wow_more_children, file, 'german')
        else:
            get_text(child, file)


def parse_url(download_url):
    split_url = download_url.split("/")
    parsed_url = []
    for elem in split_url:
        if elem != 'download_xml':
            parsed_url.append(elem)
        else:
            parsed_url.append('show')
    return "/".join(parsed_url)


# finds url id of volume. use id to map volume to pub info in csv file
def get_id(root):
    for child in root:
        if 'teiHeader' in child.tag:
            for children in child:
                if 'fileDesc' in children.tag:
                    for more_children in children:
                        if 'publicationStmt' in more_children.tag:
                            for even_more_children in more_children:
                                if 'idno' in even_more_children.tag:
                                    for wow_more_children in even_more_children:
                                        if wow_more_children.get('type') == 'URLXML':
                                            download_url = wow_more_children.text
                                            base_url = parse_url(download_url)
                                            return base_url


def parse_csv(csv_in):



def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", metavar='in-directory', action="store", help="input directory argument")
    parser.add_argument("-o", help="output directory argument", action="store")
    parser.add_argument("-csv", help="csv file with publication dates", action="store")

    try:
        args = parser.parse_args()
        common.build_out(args.o)
    except IOError:
        common.fail("IOError")

    for subdir, dirs, files in os.walk(args.i):
        for xmldoc in files:
            if xmldoc[0] != ".":
                tree = ET.parse(args.i + xmldoc)
                root = tree.getroot()
                base_url = get_id(root)
                obj = parsed.Parsed()
                get_text(root, obj)

                with open(args.o + xmldoc[:-4] + '.json', 'w', encoding='utf-8') as out:
                    out.write(parsing_help.build_json(obj))
                    out.close()


if __name__ == '__main__':
    main()