# Class for file object
class Parsed:
    def __init__(self, title='', author='', pub_info='', years="2000 ",
                 isbn='', doc_type='', chapters='', htid=''):
        self.t = title
        self.a = author
        self.p = pub_info
        self.y = years
        self.i = isbn
        self.d = doc_type
        self.ch = chapters
        self.h = htid
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


