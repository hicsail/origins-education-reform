import argparse
import tqdm
import os

from epub_conversion.utils import open_book, convert_epub_to_lines
from html.parser import HTMLParser

class Stripper(HTMLParser):
    """
    Subclass that just strips HTML from a string.
    """

    def __init__(self):
        super(Stripper, self).__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs= True
        self.fed = []

    def handle_data(self, d):
        self.fed.append(d)

    def get_data(self):
        return ''.join(self.fed)


def strip_tags(html):
    """
    Strip HTML tags from text.
    """

    s = Stripper()
    s.feed(html)
    return s.get_data()


def _parse_book(epub_file):
    """
    Convert an epub file to a list of text strings.
    """

    book = open_book(epub_file)
    lines = convert_epub_to_lines(book)

    ret = []

    for line in lines:
        if line != '' and line != '\n':
            ret.append(strip_tags(line))

    return ret


def parse_books(input_dir, output_dir):
    """
    Convert a directory of epub files to a directory of text files.
    """

    for subdir, dirs, files in os.walk(input_dir):
        for epub_f in tqdm.tqdm(files):
            if epub_f[0] != "." and epub_f[-5:] == '.epub':

                book = _parse_book("{0}/{1}".format(input_dir, epub_f))

                with open("{0}/{1}.txt".format(output_dir, epub_f[:-5]), 'w') as txt_out:

                    txt_out.write("\n".join(book))


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("-i", help="input directory", action="store")
    parser.add_argument("-o", help="output directory", action="store")

    try:
        args = parser.parse_args()
    except IOError:
        fail("IOError")

    if not os.path.isdir(args.o):
        os.mkdir(args.o)

    parse_books(args.i, args.o)

