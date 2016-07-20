import xml.etree.ElementTree as ET
import os
import argparse
import json
import re
from nltk.corpus import stopwords
import shutil

#Class for file object
class Parsed:
    def __init__(self, Title='', Author='', PubInfo='', Years="2000 ", ISBN='', DocType='', Chapters='', Content='', Text=[]):
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
    def add_year(self, year):
        self.y += year + " "

#Self-explanatory
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

#Outputs Publisher
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

#Looks for common subtags that contain text
def scanSubtagsYears(root, file):
    if root.tag == "{http://www.tei-c.org/ns/1.0}pb":
        addYears(root, file)
    if root.tag == "{http://www.tei-c.org/ns/1.0}hi":
        addYears(root, file)
    if root.tag == "{http://www.tei-c.org/ns/1.0}lb":
        addYears(root, file)

#Appends a year to a file's year field
def addYears(root, file):
    text = str(root.text) + str(root.tail)
    text = text.strip(' \t\n\r')
    text = text.replace("None", "")
    reg = re.compile("[1][7-9][0-9]{2}")
    years = reg.findall(text)
    years[:] = [s.replace(" ", "") for s in years]
    i = 0
    while i < len(years):
        file.add_year(years[i])
        i += 1

#There are four separate methods for grabbing the year of publication.
#This will likely need to be fixed in the future, but there are a lot of
#different paths though each XML file where publication years are included,
#and since these methods are recursive, I can't think of any way to trace each
#path without separating them into four distinct functions.
def getYears(root, file):
    if "publisher" in root.tag or "bibl" in root.tag or "title" in root.tag or "date" in root.tag:
        addYears(root, file)
        for child in root:
            scanSubtagsYears(child, file)
            if "date" in child.tag or "title" in child.tag:
                addYears(child, file)
                for children in child:
                    scanSubtagsYears(children, file)
    else:
        for child in root:
            getYears(child, file)

def fixYears(root, file):
    a = sorted(file.y.split())[0]
    if int(a) > 1930:
        if "front" in root.tag or "body" in root.tag:
            addYears(root, file)
            for child in root:
                scanSubtagsYears(child, file)
                if "div" in child.tag:
                    addYears(child, file)
                    for children in child:
                        scanSubtagsYears(children, file)
                        if "p" in children.tag:
                            addYears(children, file)
                            for morechildren in children:
                                scanSubtagsYears(morechildren, file)
        else:
            for child in root:
                fixYears(child, file)

def fixYearsAgain(root, file):
    a = sorted(file.y.split())[0]
    if int(a) > 1930:
        if "fileDesc" in root.tag:
            addYears(root, file)
            for child in root:
                scanSubtagsYears(child, file)
                if "sourceDesc" in child.tag:
                    addYears(child, file)
                    for children in child:
                        scanSubtagsYears(children, file)
                        if "title" in children.tag or "date" in children.tag:
                            addYears(children, file)
                            for morechildren in children:
                                scanSubtagsYears(morechildren, file)
        else:
            for child in root:
                fixYearsAgain(child, file)

def fixYearsLastTime(root, file):
    a = sorted(file.y.split())[0]
    if int(a) > 1930:
        if "text" in root.tag:
            addYears(root, file)
            for child in root:
                scanSubtagsYears(child, file)
                if "front" in child.tag:
                    addYears(child, file)
                    for children in child:
                        scanSubtagsYears(children, file)
                        if "div" in children.tag or "argument" in children.tag:
                            addYears(children, file)
                            for morechildren in children:
                                scanSubtagsYears(morechildren, file)
                                if "p" in morechildren.tag or "div" in morechildren.tag:
                                    addYears(morechildren, file)
                                    for evenmorechildren in morechildren:
                                        scanSubtagsYears(evenmorechildren, file)
                                        if "p" in evenmorechildren.tag:
                                            addYears(evenmorechildren, file)
                                            for wowmorechildren in evenmorechildren:
                                                scanSubtagsYears(wowmorechildren, file)
        else:
            for child in root:
                fixYearsLastTime(child, file)

#Helper method for ISBN method
def checkForISBN(root, file):
    test1 = str(root.text)
    test2 = str(root.tail)
    if "ISBN" in test1:
        ISBN = test1.strip(' \t\n\r')
        ISBN = ISBN.replace("None", "")
        reg = re.compile("[0-9]-?[0-9]-?[0-9]-?[0-9]-?[0-9]-?[0-9]-?[0-9]-?[0-9]-?[0-9]-?[0-9]-?")
        try:
            ISBN_clean = reg.findall(ISBN)[0]
            file.i = ISBN_clean
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

#Gets ISBN
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

#Determines whether the file is a Novel/Essay, Poetry, or Drama
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

#Helper function to write to a file object.
def addContent(root, file):
    text = str(root.text) + str(root.tail)
    text = text.strip(' \t\n\r')
    text = text.replace("None", "")
    file.add_content(text)

#Adds chapters to the file
def addChapter(root, file):
    chapter = str(root.text) + str(root.tail)
    chapter = chapter.strip(' \t\n\r')
    chapter = chapter.replace("None", "")
    file.add_chapter(chapter)

#Scans a file for its chapter titles
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


#Helper function to search for most common subtags
# and write their contents to a file object.
def scanForSubtags(root, file):
    if root.tag == "{http://www.tei-c.org/ns/1.0}pb":
        addContent(root, file)
    if root.tag == "{http://www.tei-c.org/ns/1.0}hi":
        addContent(root, file)
    if root.tag == "{http://www.tei-c.org/ns/1.0}lb":
        addContent(root, file)

#Method for grabbing text from the XML files.
#It branches off some way through if the file
#contains Poetry or Theater tags.
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

#Method for grabbing individual poems
def getPoetry(root, file):
    for child in root:
        if child.tag == "{http://www.tei-c.org/ns/1.0}l":
            addContent(child, file)
            for children in child:
                scanForSubtags(children, file)
        else:
            getPoetry(child, file)

#Grabs text from a Drama
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

def filterText(text, file):
    textList = text.strip().split()
    stripped_text = [word.strip(",._-:;\"'\\()[]0123456789!?") for word in textList]
    for i in range(len(stripped_text) - 1, -1, -1):
        if stripped_text[i] == "":
            del stripped_text[i]
    cleaned_text = [word.lower() for word in stripped_text]
    filtered_words = [word for word in cleaned_text if word not in stopwords.words('danish')]
    file.tx = filtered_words

#Gathers all the info from the parsing functions above and builds
#a JSON file out of it. It also cleans up the file a little bit, and
#checks if some fields are empty.
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
    if file.ch is None:
        file.ch = "No chapters listed"
    if file.c is None:
        file.c = ""
    file.t = file.t.replace("\n", " ")
    file.a = file.a.replace("\n", " ")
    file.p = file.p.replace("\n", " ")
    file.d = file.d.replace("\n", " ")
    file.ch = file.ch.replace("\n", " ")
    file.c = file.c.replace("\n", " ")
    file.y = sorted(file.y.split())[0] #only take the earliest year collected
    jfile = json.dumps({'1.Title': file.t, '2.Author': file.a, '3.Publisher': file.p, '4.Year Published': file.y, '5.ISBN': file.i,
                        '6.Document Type': file.d, '7.List of chapters': file.ch, '8.Full Text': file.c, '9.Filtered Text': file.tx},
                       sort_keys=True, indent=4, separators=(',', ': '), ensure_ascii=False)
    return jfile


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", metavar='in-directory', action="store", help="input directory argument")
    parser.add_argument("-o", help="output directory argument", action="store")
    parser.add_argument("-f", help="optional filtering argument", action="store_true")

    try:
        args = parser.parse_args()
    except IOError:
        pass

    if not os.path.exists(args.o):
        os.mkdir(args.o)
    else:
        shutil.rmtree(args.o)
        os.mkdir(args.o)

    for subdir, dirs, files in os.walk(args.i):
        for xmldoc in files:
            if xmldoc[0] != ".":
                tree = ET.parse(args.i + xmldoc)
                root = tree.getroot()
                obj = Parsed()
                getText(root, obj)
                text = str(obj.c)
                if text.strip() != "":
                    try:
                        with open(args.o + xmldoc[:-4] + '.json', 'w', encoding='utf-8') as out:
                            getTitleAndAuthor(root, obj)
                            getPublicationInfo(root, obj)
                            getISBN(root, obj)
                            getYears(root, obj)
                            fixYears(root, obj)
                            fixYearsAgain(root, obj)
                            fixYearsLastTime(root, obj)
                            docType(root, obj)
                            getChapters(root, obj)
                            if args.f:
                                filterText(text, obj)
                            out.write(buildJson(obj))
                            out.close()
                    except IOError:
                        pass

if __name__ == '__main__':
    main()
