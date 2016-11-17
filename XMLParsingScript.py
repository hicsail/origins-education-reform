import xml.etree.ElementTree as ET
import os, argparse, json, re, shutil
from nltk.corpus import stopwords
from multiprocessing import Pool
from nltk.stem.snowball import SnowballStemmer

# This script navigates through a directory of XML files (organized according to
# a specific template) and builds JSON files out of them. The outputted JSON files include
# separate fields for: Title, Author, Publication Info, Publication Date, ISBN Number, Chapter
# List, Full Text, Filtered Text, and Stemmed Text.

# Class for file object
class Parsed:
    def __init__(self, Title='', Author='', PubInfo='', Years="2000 ", ISBN='', DocType='', Chapters=''):
        self.t = Title
        self.a = Author
        self.p = PubInfo
        self.y = Years
        self.i = ISBN
        self.d = DocType
        self.ch = Chapters
        self.c = []
        self.cstem = []
        self.tx = []
        self.txstem = []
        self.c_sent = []
        self.tx_sent = []
        self.cstem_sent = []
        self.txstem_sent = []
    def add_content_sent(self, text):
        self.c_sent.append(text)
    def add_filtered_sent(self, text):
        self.tx_sent.append(text)
    def add_stemmed_sent(self, text):
        self.cstem_sent.append(text)
    def add_filtered_stemmed_sent(self, text):
        self.txstem_sent.append(text)
    def add_content(self, text):
        self.c.extend(text)
    def add_filtered(self, text):
        self.tx.extend(text)
    def add_stemmed(self, text):
        self.cstem.extend(text)
    def add_filtered_stemmed(self, text):
        self.txstem.extend(text)
    def add_chapter(self, chapter):
        self.ch += chapter + ", "
    def add_year(self, year):
        self.y += year + " "


# For all the "get" methods below, the 'if' statements just lead the method through paths in the XML
# document where the information that it's trying to get typically resides. For example, the
# 'getTitleAndAuthor' method looks for all tags in the XML document with the words "title" and "author" in them,
# which are themselves children of a tag called "titleStmt". It recursively searches through the XML file, which
# is to say that if it is called on a node in which it doesn't find on of the words that it's looking for,
# it will simply check all the children of that node (and so on and so on) until it gets to a node with no children.
# It will thus search the entire XML file and output only the information you want, so long as you point it to the right
# sequence of tags.


def getTitleAndAuthor(root, file):
    if "titleStmt" in root.tag:
        for child in root:
            if "title" in child.tag:
                file.t = child.text
            if "author" in child.tag:
                file.a = child.text
        return
    else:
        for child in root:
            getTitleAndAuthor(child, file)


# Outputs Publisher
def getPublicationInfo(root, file):
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
            getPublicationInfo(child, file)


# Looks for common subtags that contain text
def scanSubtagsYears(root, file):
    if root.tag == "{http://www.tei-c.org/ns/1.0}pb":
        addYears(root, file)
    if root.tag == "{http://www.tei-c.org/ns/1.0}hi":
        addYears(root, file)
    if root.tag == "{http://www.tei-c.org/ns/1.0}lb":
        addYears(root, file)


# Helper function to search for most common subtags
# and write their contents to a file object.
def scanForSubtags(root, file):
    if root.tag == "{http://www.tei-c.org/ns/1.0}pb":
        addContent(root, file)
    if root.tag == "{http://www.tei-c.org/ns/1.0}hi":
        addContent(root, file)
    if root.tag == "{http://www.tei-c.org/ns/1.0}lb":
        addContent(root, file)


# Appends a year to a file's year field
def addYears(root, file):
    text = str(root.text) + str(root.tail)
    text = text.strip(' \t\n\r')
    text = text.replace("None", "")
    reg = re.compile("[1][4-9][0-9]{2}")
    years = reg.findall(text)
    years[:] = [s.replace(" ", "") for s in years]
    for year in years:
        file.add_year(year)


# Find publication year
def getYears(root, file):
    if "publicationStmt" in root.tag:
        for child in root:
            if "publisher" in child.tag:
                addYears(child, file)
                for children in child:
                    scanSubtagsYears(children, file)
        return
    else:
        for child in root:
            getYears(child, file)


# Helper method for ISBN method
def checkForISBN(root, file):
    test1 = str(root.text)
    test2 = str(root.tail)
    if "ISBN" in test1:
        ISBN = test1.strip(' \t\n\r')
        ISBN = ISBN.replace("None", "")
        # Looks for a sequence of numbers/dashes which fits the format of an ISBN number.
        # the 're' module allows one to grab only those strings which match a particular
        # format, with the surrounding text stripped.
        reg = re.compile("[0-9]-?[0-9]-?[0-9]-?[0-9]-?[0-9]-?[0-9]-?[0-9]-?[0-9]-?[0-9]-?[0-9]-?")
        try:
            ISBN_clean = reg.findall(ISBN)[0]
            file.i = ISBN_clean
        # If nothing is returned, there will be no first element (i.e. - ISBN[0]), so
        # this exception handles that event.
        except IndexError:
            pass
    if "ISBN" in test2:
        ISBN = test2.strip(' \t\n\r')
        ISBN = ISBN.replace("None", "")
        reg = re.compile("[0-9]-?[0-9]-?[0-9]-?[0-9]-?[0-9]-?[0-9]-?[0-9]-?[0-9]-?[0-9]-?[0-9]-?")
        try:
            ISBN_clean = reg.findall(ISBN)[0]
            file.i = ISBN_clean
        except IndexError:
            pass


# Gets ISBN
def getISBN(root, file):
    if "front" in root.tag:
        for child in root:
            if "div" in child.tag:
                for children in child:
                    if "p" or "bibl" in children.tag:
                        checkForISBN(children, file)
                        for morechildren in children:
                            if morechildren.tag == "{http://www.tei-c.org/ns/1.0}pb":
                                checkForISBN(morechildren, file)
                            if morechildren.tag == "{http://www.tei-c.org/ns/1.0}hi":
                                checkForISBN(morechildren, file)
                            if morechildren.tag == "{http://www.tei-c.org/ns/1.0}lb":
                                checkForISBN(morechildren, file)



    else:
        for child in root:
            getISBN(child, file)


# Determines whether the file is a Novel/Essay, Poetry, or Drama
def docType(root, file):
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
            docType(child, file)


# Scans a file for its chapter titles
def getChapters(root, file):
    if "body" in root.tag:
        for child in root:
            if "div" in child.tag:
                for children in child:
                    if "head" in children.tag:
                        addChapter(children, file)
                    if "div" in children.tag:
                        for morechildren in children:
                            if "head" in morechildren.tag:
                                addChapter(morechildren, file)
                                for evenmorechildren in morechildren:
                                    if "emph" in evenmorechildren.tag:
                                        addChapter(evenmorechildren, file)
                                    if "hi" in evenmorechildren.tag:
                                        addChapter(evenmorechildren, file)

    else:
        for child in root:
            getChapters(child, file)


# Method for grabbing text from the XML files.
# It branches off some way through if the file
# contains Poetry or Theater tags.
def getText(root, file):
    for kid in root:
        if "body" in kid.tag or "back" in kid.tag or "front" in kid.tag:
            for child in kid:
                if child.tag == "{http://www.tei-c.org/ns/1.0}lg":
                    getPoetry(child, file)
                if "div" in child.tag:
                    for children in child:
                        if children.tag == "{http://www.tei-c.org/ns/1.0}stage":
                            getTheater(children, file)
                        if children.tag == "{http://www.tei-c.org/ns/1.0}sp":
                            getTheater(children, file)
                        if children.tag == "{http://www.tei-c.org/ns/1.0}lg":
                            getPoetry(children, file)
                        if children.tag == "{http://www.tei-c.org/ns/1.0}p":
                            addContent(children, file)
                            for morechildren in children:
                                scanForSubtags(morechildren, file)
                        if "div" in children.tag:
                            for morechildren in children:
                                if morechildren.tag == "{http://www.tei-c.org/ns/1.0}stage":
                                    getTheater(morechildren, file)
                                if morechildren.tag == "{http://www.tei-c.org/ns/1.0}sp":
                                    getTheater(morechildren, file)
                                if morechildren.tag == "{http://www.tei-c.org/ns/1.0}lg":
                                    getPoetry(morechildren, file)
                                if morechildren.tag == "{http://www.tei-c.org/ns/1.0}p":
                                    addContent(morechildren, file)
                                    for evenmorechildren in morechildren:
                                        scanForSubtags(evenmorechildren, file)
                                if "div" in morechildren.tag:
                                    for evenmorechildren in morechildren:
                                        if evenmorechildren.tag == "{http://www.tei-c.org/ns/1.0}p":
                                            addContent(evenmorechildren, file)
                                            for wowmorechildren in evenmorechildren:
                                                scanForSubtags(wowmorechildren, file)
                                        if evenmorechildren.tag == "{http://www.tei-c.org/ns/1.0}stage":
                                            getTheater(evenmorechildren, file)
                                        if evenmorechildren.tag == "{http://www.tei-c.org/ns/1.0}sp":
                                            getTheater(evenmorechildren, file)

        else:
            getText(kid, file)


# Method for grabbing individual poems
def getPoetry(root, file):
    for child in root:
        if child.tag == "{http://www.tei-c.org/ns/1.0}l":
            addContent(child, file)
            for children in child:
                scanForSubtags(children, file)
        else:
            getPoetry(child, file)


# Grabs text from a Drama
def getTheater(child, file):
    if child.tag == "{http://www.tei-c.org/ns/1.0}stage":
        addContent(child, file)
        for children in child:
            scanForSubtags(children, file)
            if children.tag == "{http://www.tei-c.org/ns/1.0}p":
                addContent(children, file)
                for morechildren in children:
                    scanForSubtags(morechildren, file)
    if child.tag == "{http://www.tei-c.org/ns/1.0}sp":
        addContent(child, file)
        for children in child:
            scanForSubtags(children, file)
            if children.tag == "{http://www.tei-c.org/ns/1.0}speaker":
                addContent(children, file)
                for morechildren in children:
                    scanForSubtags(morechildren, file)
            if children.tag == "{http://www.tei-c.org/ns/1.0}stage":
                addContent(children, file)
                for morechildren in children:
                    scanForSubtags(morechildren, file)
            if children.tag == "{http://www.tei-c.org/ns/1.0}p":
                addContent(children, file)
                for morechildren in children:
                    scanForSubtags(morechildren, file)
                    if morechildren.tag == "{http://www.tei-c.org/ns/1.0}stage":
                        addContent(morechildren, file)
                        for evenmorechildren in morechildren:
                            scanForSubtags(evenmorechildren, file)


# Add a chapter to the chapter list
def addChapter(root, file):
    chapter = str(root.text) + str(root.tail)
    t = re.split('\W[0-9]*', chapter)
    ch = " ".join(t)
    ch = ch.strip()
    file.add_chapter(ch)


# Cleans up the chapter list by getting rid of 'None' and empty entries
def filterChapters(chapters):
    ch = chapters.split(",")
    for i in range(len(ch) - 1, -1, -1):
        if ch[i].strip() == "" or ch[i].strip() == "None":
            del ch[i]
    ch_string = ", ".join(ch)
    return ch_string


# Helper function to write to a file object. If you want to add more fields
# (lemmatization, etc.) to a Parsed object, you just need to define it in the
# class definition above, write the method(s) for building it, and add it to
# this method along with the buildJson method below.


def addContent(root, file):
    text = str(root.text) + str(root.tail)
    sentences = re.split('(?<=[.!?]) +', text)
    for sentence in sentences:
        sentence = cleanText(sentence)
        if len(sentence) > 1:
            file.add_content_sent(" ".join(sentence))
            sentence_stemmed = stemText(sentence)
            file.add_stemmed_sent(" ".join(sentence_stemmed))
            sentence_filtered = filterText(sentence)
            if len(sentence_filtered) > 1:
                file.add_filtered_sent(" ".join(sentence_filtered))
                sentence_filtered_stemmed = stemText(sentence_filtered)
                file.add_filtered_stemmed_sent(" ".join(sentence_filtered_stemmed))
    text_list = cleanText(text)
    # full text
    file.add_content(text_list)
    # stem the full text
    stemmed = stemText(text_list)
    file.add_stemmed(stemmed)
    # filter the unstemmed full text
    # note: the filterText method permanently deletes elements of text_list, so if you need
    # to use the unfiltered text_list, use it above the filtered declaration below
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
        if text_list[i] == "" or text_list[i] == "None":
            del text_list[i]
        else:
            text_list[i] = text_list[i].lower()
    return text_list


# removes stop words from a text
def filterText(text_list):
    filtered_words = set(stopwords.words('danish'))
    # Loop backwards because delete changes index
    for i in range(len(text_list) - 1, -1, -1):
        # Delete empty strings or stopwords
        if text_list[i] in filtered_words:
            del text_list[i]
    return text_list


# Loop through filtered text and stem all the words
def stemText(text_list):
    # Init stemmer & array to store stemmed words
    stemmer = SnowballStemmer("danish")
    stemmed = []
    for word in text_list:
        stemmed.append(stemmer.stem(word))
    return stemmed


# Gathers all the info from the parsing functions above and builds
# a JSON file out of it. It also cleans up the file a little bit, and
# checks if some fields are empty.
def buildJson(file):
    if file.t is None:
        file.t = "No title listed"
    if file.a is None:
        file.a = "No author listed"
    if file.p is None:
        file.p = "No publisher listed"
    if file.i == '':
        file.i = "No ISBN listed"
    if file.d is None:
        file.d = "No document type"
    file.t = file.t.replace("\n", " ")
    file.a = file.a.replace("\n", " ")
    file.p = file.p.replace("\n", " ")
    file.d = file.d.replace("\n", " ")
    file.ch = filterChapters(file.ch)
    file.y = sorted(file.y.split())[0] # only take the earliest year collected
    jfile = json.dumps({'Title': file.t, 'Author': file.a, 'Publisher': file.p, 'Year Published': file.y,
                        'ISBN': file.i, 'Document Type': file.d, 'List of chapters': file.ch,
                        'Full Text': file.c, 'Full Text Stemmed': file.cstem, 'Filtered Text': file.tx,
                        'Filtered Text Stemmed': file.txstem, 'Full Sentences': file.c_sent,
                        'Filtered Sentences': file.tx_sent, 'Stemmed Sentences': file.cstem_sent,
                        'Filtered Stemmed Sentences': file.txstem_sent},
                       sort_keys=True, indent=4, separators=(',', ': '), ensure_ascii=False)
    return jfile


def parse_threaded(xmldoc, input_doc, output_doc):
    tree = ET.parse(input_doc + xmldoc)
    root = tree.getroot()
    obj = Parsed()
    getText(root, obj)
    text = "".join(obj.c)
    if text != "":
        try:
            with open(output_doc + xmldoc[:-4] + '.json', 'w', encoding='utf-8') as out:
                getTitleAndAuthor(root, obj)
                getPublicationInfo(root, obj)
                getISBN(root, obj)
                getYears(root, obj)
                docType(root, obj)
                getChapters(root, obj)
                out.write(buildJson(obj))
                out.close()
        except IOError:
            pass


def main():
    # Command line arguments.
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", metavar='in-directory', action="store", help="input directory argument")
    parser.add_argument("-o", help="output directory argument", action="store")

    try:
        args = parser.parse_args()
    except IOError:
        pass

    # Checks if the output directory already exists. If it exists, the existing directory is
    # deleted and a new directory is created in its place.
    if not os.path.exists(args.o):
        os.mkdir(args.o)
    else:
        shutil.rmtree(args.o)
        os.mkdir(args.o)

    thread_files = []

    # Grabs each XML file and does all the methods above to it, and builds up the
    # various fields for the JSON file in the process. At the end, it builds the JSON
    # file from the Parsed() object defined at the beginning.
    for subdir, dirs, files in os.walk(args.i):
        for xmldoc in files:
            if xmldoc[0] != ".":
                thread_files.append((xmldoc, args.i, args.o))
                # parse_threaded(xmldoc, args.i, args.o, args.f)

    pool = Pool()
    pool.starmap(parse_threaded, thread_files)
    pool.close()
    pool.join()

if __name__ == '__main__':
    # cProfile.runctx('main()', globals(), locals())
    main()
