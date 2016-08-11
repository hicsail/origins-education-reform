import os, zipfile, csv, json, shutil, argparse
import xml.etree.ElementTree as ET
from nltk.corpus import stopwords

#Class for file object
class Parsed:
    def __init__(self, HTID='', Title='', Author='', PubInfo='', Years='',
                 ISBN='', DocType='', Chapters='', Content='', Text=[]):
        self.h = HTID
        self.t = Title
        self.a = Author
        self.p = PubInfo
        self.y = Years
        self.i = ISBN
        self.d = DocType
        self.ch = Chapters
        self.c = Content
        self.tx = Text
    def add_content(self, text):
        self.c += text + " "
    def add_chapter(self, chapter):
        self.ch += chapter + " , "
    

def filterText(text, file):
    textList = text
    filtered_words = set(stopwords.words('danish'))
    # Strip each word of non-alphabetic characters
    # Loop backwards because delete changes index
    for i in range(len(textList) - 1, -1, -1):
        textList[i] = textList[i].strip(",._-:;\"'\\()[]0123456789!?").lower()
        # Delete empty strings or stopwords
        if textList[i] == "" or textList[i] in filtered_words:
            del textList[i]
    file.tx = textList


def getHTID(root, file):
    if "objectIdentifierValue" in root.tag:
        htid = root.text
        htid = htid.replace("/", "=")
        htid = htid.replace(":", "+")
        file.h = htid
        return
    else:
        for child in root:
            getHTID(child, file)

def getTitleAuthorPubInfo(readcsv, file):
    for row in readcsv:
        if row[0] == str(file.h):
            file.a = row[4]
            file.p = row[5]
            file.y = row[6]
            file.t = row[10]
            return

def buildJson(file):
    jfile = json.dumps({'1.Title': file.t, '2.Author': file.a, '3.Publisher': file.p, '4.Year Published': file.y, '5.ISBN': file.i,
                        '6.Document Type': file.d, '7.List of chapters': file.ch, '8.Full Text': file.c, '9.Filtered Text': file.tx},
                       sort_keys=True, indent=4, separators=(',', ': '), ensure_ascii=False)
    return jfile




def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", metavar='input directory argument', action="store", help="input directory argument")
    parser.add_argument("-o", help="output directory argument", action="store")
    parser.add_argument("-c", help="CSV-file location", action="store")
    parser.add_argument("-d", help="document type", action="store")


    try:
        args = parser.parse_args()
    except IOError:
        pass

    def fail(msg):
        print(msg)
        os._exit(1)

    documentType = args.d

    if not os.path.exists(args.o):
        os.mkdir(args.o)
    else:
        shutil.rmtree(args.o)
        os.mkdir(args.o)

    for folder, subfolders, files in os.walk(args.i):
        if not subfolders:
            obj = Parsed()
            # This next line will most likely be a command line input value,
            # since there isn't really anythin in the data or metadata to
            # distinguish document type.
            obj.d = str(documentType)
            for file in files:
                if file[-4:] == ".xml":
                    #concatenate folder & file with f slash btwn (filepath to xml)
                    xml = folder + "/" + file
                    tree = ET.parse(xml)
                    root = tree.getroot()
                    getHTID(root, obj)

                if file[-4:] == ".zip":
                    #concatenate folder & file with f slash btwn (filepath to zip)
                    with zipfile.ZipFile(folder + "/" + file, 'r') as zf:
                        for file in zf.namelist():
                            if file[-4:] == ".txt":
                                text = zf.read(file).decode('utf-8')
                                obj.add_content(text)
            text = str(obj.c)
            filterText(text, obj)

            with open(args.c, 'r', encoding='utf-8') as csvfile:
                readCSV = csv.reader(csvfile, delimiter=',')
                try:
                    getTitleAuthorPubInfo(readCSV, obj)
                except UnicodeDecodeError:
                    fail("Make sure the CSV files you are referencing are UTF-8 encoded.")
            csvfile.close()

            with open(args.o + str(obj.h) + ".json", 'w', encoding='utf-8') as out:
                out.write(buildJson(obj))
                out.close()

if __name__ == '__main__':
    main()
