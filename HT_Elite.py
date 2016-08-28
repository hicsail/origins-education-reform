import csv, argparse, os, shutil, json, zipfile, re
import xml.etree.ElementTree as ET
from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer


class Parsed:
    def __init__(self, HTID= '', Title='', Author='', PubInfo='', Years=" ", ISBN='', DocType='', Chapters=''):
        self.h = HTID
        self.t = Title
        self.a = Author
        self.p = PubInfo
        self.y = Years
        self.i = ISBN
        self.d = DocType
        self.ch = Chapters
        self.c = []
        self.tx = []
        self.cstem = []
        self.txstem = []
    def add_chapter(self, chapter):
        self.ch += chapter + ", "
    def add_content(self, text):
        self.c.extend(text)
    def add_filtered(self, text):
        self.tx.extend(text)
    def add_stemmed(self, text):
        self.cstem.extend(text)
    def add_filtered_stemmed(self, text):
        self.txstem.extend(text)


# Gathers all the info from the parsing functions above and builds
# a JSON file out of it.
def buildJson(file):
    jfile = json.dumps({'Title': file.t, 'Author': file.a, 'Publisher': file.p, 'Year Published': file.y,
                        'ISBN': file.i, 'Document Type': file.d, 'List of chapters': file.ch, 'Full Text': file.c,
                        'Filtered Text': file.tx,'Filtered Text Stemmed': file.txstem, 'Full Text Stemmed': file.cstem},
                       sort_keys=True, indent=4, separators=(',', ': '), ensure_ascii=False)
    return jfile


def scanForHTIDs(root):
    if "objectIdentifierValue" in root.tag:
        htid = root.text
        return htid
    else:
        for child in root:
            htid = scanForHTIDs(child)
            if htid is not None:
                return htid


def testFileHTID(htid, htids):
    if htid in htids:
        return True
    else:
        return False


def buildHTIDs(in_dir):
    htids = set()
    for subdir, dirs, files in os.walk(in_dir):
        for csvfile in files:
            if csvfile[0] != '.':
                with open(in_dir + csvfile, 'r') as csv_in:
                    readCSV = csv.reader(csv_in, delimiter=',')
                    for row in readCSV:
                        if row[0] != 'htid':
                            id = row[0]
                            id = id.replace("+", ":")
                            id = id.replace("=", "/")
                            htids.add(id)
    return htids


# Helper function to write to a file object. If you want to add more fields
# (lemmatization, etc.) to a Parsed object, you just need to define it in the
# class definition above, write the method(s) for building it, and add it to
# this method along with the buildJson method below.
def addContent(text, file):
    text_list = cleanText(text)
    # full text
    file.add_content(text_list)
    # stem the full text
    stemmed = stemText(text_list)
    file.add_stemmed(stemmed)
    # filter the unstemmed full text
    # note: the filterText method permanently deletes elements of text_list, so if you need
    # to use the unfiltered text_list for anything, use it above the filtered declaration below
    filtered = filterText(text_list)
    file.add_filtered(filtered)
    # stem the filtered text
    filtered_stemmed = stemText(filtered)
    file.add_filtered_stemmed(filtered_stemmed)


# converts all letters to lowercase, removes non-alphabetic characters, removes empty strings
def cleanText(text):
    # strip each word of non-alphabetic characters
    text_list = re.split('\W[0-9]*', text)
    # Loop backwards because delete changes index
    for i in range(len(text_list) - 1, -1, -1):
        # Delete empty strings
        if text_list[i] == "":
            del text_list[i]
        else:
            text_list[i] = text_list[i].lower()
    return text_list


# removes stop words from a text
def filterText(text_list):
    filtered_words = set(stopwords.words('english'))
    # Loop backwards because delete changes index
    for i in range(len(text_list) - 1, -1, -1):
        # Delete empty strings or stopwords
        if text_list[i] in filtered_words:
            del text_list[i]
    return text_list


# Loop through filtered text and stem all the words
def stemText(text_list):
    # Init stemmer & array to store stemmed words
    stemmer = SnowballStemmer('english')
    stemmed = []
    for word in text_list:
        stemmed.append(stemmer.stem(word))
    return stemmed


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-e", metavar='in-directory fpr Elite CSV files', action="store",
                        help="input directory argument")
    parser.add_argument("-o", help='output directory', action="store")
    parser.add_argument("-x", help='in-directory for HT files', action="store")

    try:
        args = parser.parse_args()
    except IOError:
        pass

    def fail(msg):
        print(msg)
        os._exit(1)

    if not os.path.exists(args.o):
        os.mkdir(args.o)
    else:
        shutil.rmtree(args.o)
        os.mkdir(args.o)

    htids = buildHTIDs(args.e)

    for folder, subfolders, files in os.walk(args.x):
        if not subfolders:
            for file in files:
                if file[-4:] == ".xml":
                    # concatenate folder & file with f slash btwn (filepath to xml)
                    xml = folder + "/" + file
                    tree = ET.parse(xml)
                    root = tree.getroot()
                    htid = scanForHTIDs(root)
                    if testFileHTID(htid, htids):
                        # build json object
                        obj = Parsed()
                        htid = htid.replace("/", "=")
                        htid = htid.replace(":", "+")
                        # replace periods for file-naming
                        htid_filename = htid.replace(".", "_")
                        obj.h = htid_filename
                        for file_two in files:
                            if file_two[-4:] == ".zip":
                                with zipfile.ZipFile(folder + "/" + file_two, 'r') as zf:
                                    for file_three in zf.namelist():
                                        if file_three[-4:] == ".txt":
                                            text = zf.read(file_three).decode('utf-8')
                                            addContent(text, obj)
                                for subdir, dirs, files_two in os.walk(args.e):
                                    for csv_file in files_two:
                                        if csv_file[0] != '.':
                                            with open(args.e + csv_file, 'r') as csvfile:
                                                readCSV = csv.reader(csvfile, delimiter=',')
                                                for row in readCSV:
                                                    if row[0] == htid:
                                                        try:
                                                            obj.a = row[4]
                                                            obj.p = row[5]
                                                            obj.y = row[6]
                                                            obj.t = row[10]
                                                            try:
                                                                obj.d = row[19]
                                                            except IndexError:
                                                                obj.d = "No Doctype Listed"
                                                        except UnicodeDecodeError:
                                                            fail("Make sure the CSV files you are referencing are UTF-8 encoded.")
                                with open(args.o + str(obj.h) + ".json", 'w', encoding='utf-8') as out:
                                    out.write(buildJson(obj))


if __name__ == '__main__':
    main()
