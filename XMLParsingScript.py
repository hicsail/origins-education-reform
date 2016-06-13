import xml.etree.ElementTree as ET
import os
import argparse
import json

#Class for file object
class Parsed:
    def __init__(self, Title, Author, PubInfo, ISBN, DocType, Chapters, Content):
        self.t = Title
        self.a = Author
        self.p = PubInfo
        self.i = ISBN
        self.d = DocType
        self.ch = Chapters
        self.c = Content
    def add_content(self, text):
        self.c += text + " "
    def add_chapter(self, chapter):
        self.ch += chapter + " , "

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

#Helper method for ISBN method
def checkForISBN(root, file):
    test1 = str(root.text)
    test2 = str(root.tail)
    if "ISBN" in test1:
        ISBN = test1.strip(' \t\n\r')
        ISBN = ISBN.replace("None", "")
        file.i = ISBN
    if "ISBN" in test2:
        ISBN = test2.strip(' \t\n\r')
        ISBN = ISBN.replace("None", "")
        file.i = ISBN

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
        file.c = "No text listed"
    file.t = file.t.replace("\n", " ")
    file.a = file.a.replace("\n", " ")
    file.p = file.p.replace("\n", " ")
    file.i = file.i.replace("\n", " ")
    file.d = file.d.replace("\n", " ")
    file.ch = file.ch.replace("\n", " ")
    file.c = file.c.replace("\n", " ")
    jfile = json.dumps({'1.Title': file.t, '2.Author': file.a, '3.Publisher': file.p, '4.ISBN': file.i,
                        '5.Document Type': file.d, '6.List of chapters': file.ch, '7.Full Text': file.c},
                       sort_keys=True, indent=4, separators=(',', ': '))
    return jfile


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", metavar='in-directory', action="store", help="input directory argument")
    parser.add_argument("-o", help="output directory argument", action="store")

    try:
        args = parser.parse_args()
    except IOError:
        pass

    os.mkdir(args.o)

    for subdir, dirs, files in os.walk(args.i):
        for xmldoc in files:
            try:
                with open(args.o + xmldoc[:-4] + '.json', 'w') as out:
                    tree = ET.parse(args.i + "/" + xmldoc)
                    root = tree.getroot()
                    obj = Parsed('','','','','','','')
                    getTitleAndAuthor(root, obj)
                    getPublicationInfo(root, obj)
                    getISBN(root, obj)
                    docType(root, obj)
                    getChapters(root, obj)
                    getText(root, obj)
                    out.write(buildJson(obj))
                    out.close()
            except IOError:
                pass

if __name__ == '__main__':
    main()



