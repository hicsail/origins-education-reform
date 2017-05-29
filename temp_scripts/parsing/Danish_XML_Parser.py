import argparse, os, re, csv
import xml.etree.ElementTree as ET
from multiprocessing import Pool
from nlp_scripts import common, parsing_help, parsed


# This script navigates through a directory of XML files (organized according to
# a specific template) and builds JSON files out of them. The outputted JSON files include
# separate fields for: Title, Author, Publication Info, Publication Date, ISBN Number, Chapter
# List, Full Text, Filtered Text, and Stemmed Text.


def get_title_and_author(root, file):
    if "titleStmt" in root.tag:
        for child in root:
            if "title" in child.tag:
                file.t = child.text
            if "author" in child.tag:
                file.a = child.text
        return
    else:
        for child in root:
            get_title_and_author(child, file)


# Outputs Publisher
def get_publication_info(root, file):
    if "publicationStmt" in root.tag:
        for child in root:
            if "publisher" in child.tag:
                try:
                    file.p = child.text
                except:
                    file.p = "No publisher listed"
        return
    else:
        for child in root:
            get_publication_info(child, file)


# Helper function to search for most common subtags
# and write their contents to a file object.
def scan_for_subtags(root, file):
    if root.tag == "{http://www.tei-c.org/ns/1.0}pb":
        parsing_help.add_xml_content(root, file, "danish")
    if root.tag == "{http://www.tei-c.org/ns/1.0}hi":
        parsing_help.add_xml_content(root, file, "danish")
    if root.tag == "{http://www.tei-c.org/ns/1.0}lb":
        parsing_help.add_xml_content(root, file, "danish")


# Helper method for ISBN method
def check_for_isbn(root, file):
    test1 = str(root.text)
    test2 = str(root.tail)
    if "ISBN" in test1:
        isbn = test1.strip(' \t\n\r')
        isbn = isbn.replace("None", "")
        # Looks for a sequence of numbers/dashes which fits the format of an ISBN number.
        # the 're' module allows one to grab only those strings which match a particular
        # format, with the surrounding text stripped.
        reg = re.compile("[0-9]-?[0-9]-?[0-9]-?[0-9]-?[0-9]-?[0-9]-?[0-9]-?[0-9]-?[0-9]-?[0-9]-?")
        try:
            isbn_clean = reg.findall(isbn)[0]
            file.i = isbn_clean
        # If nothing is returned, there will be no first element (i.e. - ISBN[0]), so
        # this exception handles that event.
        except IndexError:
            pass
    if "ISBN" in test2:
        isbn = test2.strip(' \t\n\r')
        isbn = isbn.replace("None", "")
        reg = re.compile("[0-9]-?[0-9]-?[0-9]-?[0-9]-?[0-9]-?[0-9]-?[0-9]-?[0-9]-?[0-9]-?[0-9]-?")
        try:
            isbn_clean = reg.findall(isbn)[0]
            file.i = isbn_clean
        except IndexError:
            pass


# Gets ISBN
def get_isbn(root, file):
    if "front" in root.tag:
        for child in root:
            if "div" in child.tag:
                for children in child:
                    if "p" or "bibl" in children.tag:
                        check_for_isbn(children, file)
                        for morechildren in children:
                            if morechildren.tag == "{http://www.tei-c.org/ns/1.0}pb":
                                check_for_isbn(morechildren, file)
                            if morechildren.tag == "{http://www.tei-c.org/ns/1.0}hi":
                                check_for_isbn(morechildren, file)
                            if morechildren.tag == "{http://www.tei-c.org/ns/1.0}lb":
                                check_for_isbn(morechildren, file)
    else:
        for child in root:
            get_isbn(child, file)


# Determines whether the file is a Novel/Essay, Poetry, or Drama
def doc_type(root, file):
    if "body" in root.tag:
        for child in root:
            if "div" in child.tag:
                for children in child:
                    if children.tag == "{http://www.tei-c.org/ns/1.0}p":
                        file.d = "Novel or Essay"
                    if children.tag == "{http://www.tei-c.org/ns/1.0}lg":
                        file.d = "Poetry"
                    if children.tag == "{http://www.tei-c.org/ns/1.0}stage":
                        file.d = "Drama"
                    if "div" in children.tag:
                        for morechildren in children:
                            if morechildren.tag == "{http://www.tei-c.org/ns/1.0}p":
                                file.d = "Novel or Essay"
                            if morechildren.tag == "{http://www.tei-c.org/ns/1.0}lg":
                                file.d = "Poetry"
                            if morechildren.tag == "{http://www.tei-c.org/ns/1.0}stage":
                                file.d = "Drama"
    else:
        for child in root:
            doc_type(child, file)


# Scans a file for its chapter titles
def get_chapters(root, file):
    if "body" in root.tag:
        for child in root:
            if "div" in child.tag:
                for children in child:
                    if "head" in children.tag:
                        add_chapter(children, file)
                    if "div" in children.tag:
                        for morechildren in children:
                            if "head" in morechildren.tag:
                                add_chapter(morechildren, file)
                                for evenmorechildren in morechildren:
                                    if "emph" in evenmorechildren.tag:
                                        add_chapter(evenmorechildren, file)
                                    if "hi" in evenmorechildren.tag:
                                        add_chapter(evenmorechildren, file)
    else:
        for child in root:
            get_chapters(child, file)


# Method for grabbing text from the XML files. It branches off
# some way through if the file contains Poetry or Theater tags.
def get_text(root, file):
    for kid in root:
        if "body" in kid.tag or "back" in kid.tag or "front" in kid.tag:
            for child in kid:
                if child.tag == "{http://www.tei-c.org/ns/1.0}lg":
                    get_poetry(child, file)
                if "div" in child.tag:
                    for children in child:
                        if children.tag == "{http://www.tei-c.org/ns/1.0}stage":
                            get_theater(children, file)
                        if children.tag == "{http://www.tei-c.org/ns/1.0}sp":
                            get_theater(children, file)
                        if children.tag == "{http://www.tei-c.org/ns/1.0}lg":
                            get_poetry(children, file)
                        if children.tag == "{http://www.tei-c.org/ns/1.0}p":
                            parsing_help.add_xml_content(children, file, "danish")
                            for morechildren in children:
                                scan_for_subtags(morechildren, file)
                        if "div" in children.tag:
                            for morechildren in children:
                                if morechildren.tag == "{http://www.tei-c.org/ns/1.0}stage":
                                    get_theater(morechildren, file)
                                if morechildren.tag == "{http://www.tei-c.org/ns/1.0}sp":
                                    get_theater(morechildren, file)
                                if morechildren.tag == "{http://www.tei-c.org/ns/1.0}lg":
                                    get_poetry(morechildren, file)
                                if morechildren.tag == "{http://www.tei-c.org/ns/1.0}p":
                                    parsing_help.add_xml_content(morechildren, file, "danish")
                                    for evenmorechildren in morechildren:
                                        scan_for_subtags(evenmorechildren, file)
                                if "div" in morechildren.tag:
                                    for evenmorechildren in morechildren:
                                        if evenmorechildren.tag == "{http://www.tei-c.org/ns/1.0}p":
                                            parsing_help.add_xml_content(evenmorechildren, file, "danish")
                                            for wowmorechildren in evenmorechildren:
                                                scan_for_subtags(wowmorechildren, file)
                                        if evenmorechildren.tag == "{http://www.tei-c.org/ns/1.0}stage":
                                            get_theater(evenmorechildren, file)
                                        if evenmorechildren.tag == "{http://www.tei-c.org/ns/1.0}sp":
                                            get_theater(evenmorechildren, file)
        else:
            get_text(kid, file)


# Method for grabbing individual poems
def get_poetry(root, file):
    for child in root:
        if child.tag == "{http://www.tei-c.org/ns/1.0}l":
            parsing_help.add_xml_content(child, file, "danish")
            for children in child:
                scan_for_subtags(children, file)
        else:
            get_poetry(child, file)


# Grabs text from a Drama
def get_theater(child, file):
    if child.tag == "{http://www.tei-c.org/ns/1.0}stage":
        parsing_help.add_xml_content(child, file, "danish")
        for children in child:
            scan_for_subtags(children, file)
            if children.tag == "{http://www.tei-c.org/ns/1.0}p":
                parsing_help.add_xml_content(children, file, "danish")
                for morechildren in children:
                    scan_for_subtags(morechildren, file)
    if child.tag == "{http://www.tei-c.org/ns/1.0}sp":
        parsing_help.add_xml_content(child, file, "danish")
        for children in child:
            scan_for_subtags(children, file)
            if children.tag == "{http://www.tei-c.org/ns/1.0}speaker":
                parsing_help.add_xml_content(children, file, "danish")
                for morechildren in children:
                    scan_for_subtags(morechildren, file)
            if children.tag == "{http://www.tei-c.org/ns/1.0}stage":
                parsing_help.add_xml_content(children, file, "danish")
                for morechildren in children:
                    scan_for_subtags(morechildren, file)
            if children.tag == "{http://www.tei-c.org/ns/1.0}p":
                parsing_help.add_xml_content(children, file, "danish")
                for morechildren in children:
                    scan_for_subtags(morechildren, file)
                    if morechildren.tag == "{http://www.tei-c.org/ns/1.0}stage":
                        parsing_help.add_xml_content(morechildren, file, "danish")
                        for evenmorechildren in morechildren:
                            scan_for_subtags(evenmorechildren, file)


# Add a chapter to the chapter list
def add_chapter(root, file):
    chapter = str(root.text) + str(root.tail)
    t = re.split('\W[0-9]*', chapter)
    ch = " ".join(t)
    ch = ch.strip()
    file.add_chapter(ch)


def get_pub_dates(csv_in):
    refs = {}
    with open(csv_in, 'r', encoding='utf-8') as csv_in:
        read_csv = csv.reader(csv_in, delimiter=',')
        for row in read_csv:
            if row[0] != 'filename':
                try:
                    refs[row[0]] = row[1]
                except UnicodeDecodeError:
                    common.fail("Make sure the CSV files you are "
                                "referencing are UTF-8 encoded.")
    return refs


def parse_threaded(xml_doc, input_doc, output_doc, csv_in):
    refs = get_pub_dates(csv_in)
    tree = ET.parse(input_doc + xml_doc)
    root = tree.getroot()
    obj = parsed.Parsed()
    get_text(root, obj)
    text = "".join(obj.c)
    if text != "":
        try:
            with open(output_doc + xml_doc[:-4] + '.json', 'w', encoding='utf-8') as out:
                get_title_and_author(root, obj)
                get_publication_info(root, obj)
                get_isbn(root, obj)
                obj.y = refs[xml_doc]
                doc_type(root, obj)
                get_chapters(root, obj)
                out.write(parsing_help.build_json(obj))
                out.close()
        except IOError:
            pass


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", metavar='in-directory', action="store", help="input directory argument")
    parser.add_argument("-o", help="output directory argument", action="store")
    parser.add_argument("-csv", help="csv file with publication dates", action="store")

    try:
        args = parser.parse_args()
    except IOError:
        common.fail("IOError")

    if args.i is None:
        common.fail("Please specify input (-i) directory.")
    if args.o is None:
        common.fail("Please specify output (-o) directory.")
    if args.csv is None:
        common.fail("Please specify csv (-csv) directory.")

    common.build_out(args.o)

    thread_files = []

    # Grabs each XML file and does all the methods above to it, and builds up the
    # various fields for the JSON file in the process. At the end, it builds the JSON
    # file from the Parsed() object defined at the beginning.
    for subdir, dirs, files in os.walk(args.i):
        for xmldoc in files:
            if xmldoc[0] != ".":
                thread_files.append((xmldoc, args.i, args.o, args.csv))

    pool = Pool()
    pool.starmap(parse_threaded, thread_files)
    pool.close()
    pool.join()

if __name__ == '__main__':
    main()
