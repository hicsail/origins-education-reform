import xml.etree.ElementTree as ET

'''
For right now this script just outputs text files. I'll add the methods
for converting it to JSON soon.
I also need to finish the methods for grabbing chapter titles. The ones I have are having 
issues with the Plays.
'''

#Until I add I/O, you just need to copy the XML
#file you want to convert into the same directory
#as this script and run it this way
tree = ET.parse("examplescript.xml")

root = tree.getroot()

out = open('workfile', 'w')

#Class for file object
class Parsed:
    def __init__(self, Title, Author, PubInfo, ISBN, DocType, Content):
        self.t = Title
        self.a = Author
        self.p = PubInfo
        self.i = ISBN
        self.d = DocType
        self.c = Content
    def add_content(self, text):
        self.c += text + "\n"


file = Parsed('','','','','','')

#Self-explanatory
def getTitleAndAuthor(root):
    if "titleStmt" in root.tag:
        for child in root:
            if "title" in child.tag:
                file.t = child.text
            if "author" in child.tag:
                file.a = child.text
        return
    else:
        for child in root:
            getTitleAndAuthor(child)

#Outputs Publisher
def getPublicationInfo(root):
    if "publicationStmt" in root.tag:
        for child in root:
            if "publisher" in child.tag:
                file.p = child.text
        return
    else:
        for child in root:
            getPublicationInfo(child)

#Helper method for ISBN method
def checkForISBN(root):
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
def getISBN(root):
    if "front" in root.tag:
        for child in root:
            if "div" in child.tag:
                for children in child:
                    if "p" or "bibl" in children.tag:
                        checkForISBN(children)
                        for morechildren in children:
                            if morechildren.tag == "{http://www.tei-c.org/ns/1.0}pb":
                                checkForISBN(morechildren)
                            if morechildren.tag == "{http://www.tei-c.org/ns/1.0}hi":
                                checkForISBN(morechildren)
                            if morechildren.tag == "{http://www.tei-c.org/ns/1.0}lb":
                                checkForISBN(morechildren)



    else:
        for child in root:
            getISBN(child)

#Determines whether the file is a Novel/Essay, Poetry, or Drama
def docType(root):
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
            docType(child)

#Helper function to write to a file object.
def addContent(root):
    text = str(root.text) + str(root.tail)
    text = text.strip(' \t\n\r')
    text = text.replace("None", "")
    file.add_content(text)

#Helper function to search for most common subtags
# and write their contents to a file object.
def scanForSubtags(root):
    if root.tag == "{http://www.tei-c.org/ns/1.0}pb":
        addContent(root)
    if root.tag == "{http://www.tei-c.org/ns/1.0}hi":
        addContent(root)
    if root.tag == "{http://www.tei-c.org/ns/1.0}lb":
        addContent(root)

#Method for grabbing text from the XML files.
#It branches off some way through if the file
#contains Poetry or Theater tags.
def getText(root):
    for kid in root:
        if "body" in kid.tag or "back" in kid.tag or "front" in kid.tag:
            for child in kid:
                if child.tag == "{http://www.tei-c.org/ns/1.0}lg":
                    getPoetry(child)
                if "div" in child.tag:
                    for children in child:
                        if children.tag == "{http://www.tei-c.org/ns/1.0}stage":
                            getTheater(children)
                        if children.tag == "{http://www.tei-c.org/ns/1.0}sp":
                            getTheater(children)
                        if children.tag == "{http://www.tei-c.org/ns/1.0}lg":
                            getPoetry(children)
                        if children.tag == "{http://www.tei-c.org/ns/1.0}p":
                            addContent(children)
                            for morechildren in children:
                                scanForSubtags(morechildren)
                        if "div" in children.tag:
                            for morechildren in children:
                                if morechildren.tag == "{http://www.tei-c.org/ns/1.0}stage":
                                    getTheater(morechildren)
                                if morechildren.tag == "{http://www.tei-c.org/ns/1.0}sp":
                                    getTheater(morechildren)
                                if morechildren.tag == "{http://www.tei-c.org/ns/1.0}lg":
                                    getPoetry(morechildren)
                                if morechildren.tag == "{http://www.tei-c.org/ns/1.0}p":
                                    addContent(morechildren)
                                    for evenmorechildren in morechildren:
                                        scanForSubtags(evenmorechildren)
                                if "div" in morechildren.tag:
                                    for evenmorechildren in morechildren:
                                        if evenmorechildren.tag == "{http://www.tei-c.org/ns/1.0}p":
                                            addContent(evenmorechildren)
                                            for wowmorechildren in evenmorechildren:
                                                scanForSubtags(wowmorechildren)
                                        if evenmorechildren.tag == "{http://www.tei-c.org/ns/1.0}stage":
                                            getTheater(evenmorechildren)
                                        if evenmorechildren.tag == "{http://www.tei-c.org/ns/1.0}sp":
                                            getTheater(evenmorechildren)

        else:
            getText(kid)

#Method for grabbing individual poems
def getPoetry(root):
    for child in root:
        if child.tag == "{http://www.tei-c.org/ns/1.0}l":
            addContent(child)
            for children in child:
                scanForSubtags(children)
        else:
            getPoetry(child)

#Grabs chapters from a Drama
def getTheater(child):
    if child.tag == "{http://www.tei-c.org/ns/1.0}stage":
        addContent(child)
        for children in child:
            scanForSubtags(children)
            if children.tag == "{http://www.tei-c.org/ns/1.0}p":
                addContent(children)
                for morechildren in children:
                    scanForSubtags(morechildren)
    if child.tag == "{http://www.tei-c.org/ns/1.0}sp":
        addContent(child)
        for children in child:
            scanForSubtags(children)
            if children.tag == "{http://www.tei-c.org/ns/1.0}speaker":
                addContent(children)
                for morechildren in children:
                    scanForSubtags(morechildren)
            if children.tag == "{http://www.tei-c.org/ns/1.0}stage":
                addContent(children)
                for morechildren in children:
                    scanForSubtags(morechildren)
            if children.tag == "{http://www.tei-c.org/ns/1.0}p":
                addContent(children)
                for morechildren in children:
                    scanForSubtags(morechildren)
                    if morechildren.tag == "{http://www.tei-c.org/ns/1.0}stage":
                        addContent(morechildren)
                        for evenmorechildren in morechildren:
                            scanForSubtags(evenmorechildren)

getTitleAndAuthor(root)
getPublicationInfo(root)
getISBN(root)
docType(root)
getText(root)
out.write("Title: " + file.t + "\n")
out.write("Author: " + file.a + "\n")
out.write("Publisher: " + file.p + "\n")
if file.i == '':
    out.write("No ISBN for this document")
else:
    out.write("ISBN: " + file.i + "\n")
out.write("Document Type: " + file.d + "\n")
out.write("Full text:\n" + file.c)







