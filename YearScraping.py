import xml.etree.ElementTree as ET
import os
import re
import argparse

class Parsed:
    def __init__(self, XMLDoc='', Title='', Author='', Years='', Content=''):
        self.x = XMLDoc
        self.t = Title
        self.a = Author
        self.y = Years
        self.c = Content
    def add_content(self, text):
        self.c += text + " "
    def add_year(self, year):
        self.y += year + " / "

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

def scanSubtagsYears(root, file):
    if root.tag == "{http://www.tei-c.org/ns/1.0}pb":
        addYears(root, file)
    if root.tag == "{http://www.tei-c.org/ns/1.0}hi":
        addYears(root, file)
    if root.tag == "{http://www.tei-c.org/ns/1.0}lb":
        addYears(root, file)

def addYears(root, file):
    text = str(root.text) + " " + str(root.tail)
    text = text.strip(' \t\n\r')
    text = text.replace("None", "")
    reg = re.compile("[1][6-9][0-9]{2}")
    years = reg.findall(text)
    years[:] = [s.replace(" ", "") for s in years]
    i = 0
    while i < len(years):
        file.add_year(years[i])
        i += 1
        
#Very simplified version of the year-grabbing methods from XMLParsingScript.py
def getYears(root, file):
    if "sourceDesc" in root.tag:
        addYears(root, file)
        for child in root:
            scanSubtagsYears(child, file)
            addYears(child, file)
            for children in child:
                scanSubtagsYears(children, file)
                addYears(children, file)
    else:
        for child in root:
            getYears(child, file)

#Helper function to write to a file object.
def addContent(root, file):
    text = str(root.text) + str(root.tail)
    text = text.strip(' \t\n\r')
    text = text.replace("None", "")
    file.add_content(text)

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

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", metavar='in-directory', action="store", help="input directory argument")
    parser.add_argument("-o", help="output directory argument", action="store")

    try:
        args = parser.parse_args()
    except IOError:
        pass

    try:
        with open(args.o + '.txt', 'w') as out:
            for subdir, dirs, files in os.walk(args.i):
                i = 1
                for xmldoc in files:
                    tree = ET.parse(args.i + "/" + xmldoc)
                    root = tree.getroot()
                    obj = Parsed()
                    obj.x = str(xmldoc)
                    getTitleAndAuthor(root, obj)
                    getYears(root, obj)
                    getText(root, obj)
                    obj.c = obj.c.replace("\n", " ")
                    text = obj.c
                    if text.strip() == "":
                        pass
                    else:
                        out.write(str(i) + ": " + obj.x + "\n")
                        try:
                            out.write("Title: " + obj.t + "\n")
                        except TypeError:
                            out.write("No title listed for this document" + "\n")
                        try:
                            out.write("Author: " + obj.a + "\n")
                        except TypeError:
                            out.write("No author listed for this document" + "\n")
                        try:
                            out.write("Year(s) of publication: " + obj.y + "\n")
                        except TypeError:
                            out.write("No year of publication listed for this document" + "\n")
                        out.write("\n")
                        i += 1
    except IOError:
        pass

if __name__ == '__main__':
    main()
