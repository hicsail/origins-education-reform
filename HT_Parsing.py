import os, zipfile, csv, json, shutil, argparse, re, time
import xml.etree.ElementTree as ET
from nltk.corpus import stopwords
from multiprocessing import Pool


#Class for file object
class Parsed:
    def __init__(self, HTID='', Title='', Author='', PubInfo='', Years='',
                 ISBN='', DocType='', Chapters=''):
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
    def add_content(self, text):
        text = re.split('\n|\s|\r', text)
        self.c.extend(text)
    def add_chapter(self, chapter):
        self.ch += chapter + " , "


def filterText(text):
    textList = text
    filtered_words = set(stopwords.words('english'))
    # Strip each word of non-alphabetic characters
    # Loop backwards because delete changes index
    for i in range(len(textList) - 1, -1, -1):
        textList[i] = textList[i].strip(",._-:;\"'\\()[]0123456789!?").lower()
        # Delete empty strings or stopwords
        if textList[i] == "" or textList[i] in filtered_words:
            del textList[i]
    return textList


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
            try:
                file.d = row[19]
            except IndexError:
                file.d = "No Doctype Listed"
            return


def buildJson(file):
    jfile = json.dumps({'1.Title': file.t, '2.Author': file.a, '3.Publisher': file.p, '4.Year Published': file.y, '5.ISBN': file.i,
                        '6.Document Type': file.d, '7.List of chapters': file.ch, '8.Full Text': '', '9.Filtered Text': file.tx},
                       sort_keys=True, indent=4, separators=(',', ': '), ensure_ascii=False)
    return jfile


def parse_files_threaded(folder, files, csv_file, output_dir):
    obj = Parsed()
    # Grab HTID & full text
    for file in files:
        if file[-4:] == ".xml":
            #concatenate folder & file with f slash btwn (filepath to xml)
            xml = folder + "/" + file
            tree = ET.parse(xml)
            root = tree.getroot()
            getHTID(root, obj)
        if file[-4:] == ".zip":
            with zipfile.ZipFile(folder + "/" + file, 'r') as zf:
                for file in zf.namelist():
                    if file[-4:] == ".txt":
                        text = zf.read(file).decode('utf-8')
                        obj.add_content(text)
    # Filter raw text, populate filtered text field
    obj.tx = filterText(obj.c)
    # Use HTID from above to find bibliographical info in
    # the CSV file provided by the user
    with open(csv_file, 'r', encoding='utf-8') as csvfile:
        readCSV = csv.reader(csvfile, delimiter=',')
        try:
            getTitleAuthorPubInfo(readCSV, obj)
        except UnicodeDecodeError:
            print("Make sure the CSV files you are referencing are UTF-8 encoded.")

    # Write to Json file
    with open(output_dir + str(obj.h) + ".json", 'w', encoding='utf-8') as out:
        out.write(buildJson(obj))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", metavar='input directory argument', action="store", help="input directory argument")
    parser.add_argument("-o", help="output directory argument", action="store")
    parser.add_argument("-c", help="CSV-file location", action="store")


    try:
        args = parser.parse_args()
    except IOError:
        pass

    if not os.path.exists(args.o):
        os.mkdir(args.o)
    else:
        shutil.rmtree(args.o)
        os.mkdir(args.o)

    docs = []
    start = time.time()
    for folder, subfolders, files in os.walk(args.i):
        if not subfolders:
            docs.append((folder, files, args.c, args.o))

    pool = Pool()
    pool.starmap(parse_files_threaded, docs)
    pool.close()
    pool.join()

    print('Finished parsing data: {0:f} s\n'.format(time.time() - start))

if __name__ == '__main__':
    main()
