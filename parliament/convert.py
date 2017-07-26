from nlp_scripts import parsing_help, parsed, common
import argparse, os, json
from multiprocessing import Pool


# assumes yyyy-mm-dd type input
def parse_date(year_string):
    date = year_string.split('-')[0]
    return date


# assumes ['sent-1', 'sent-2', ... , 'sent-n'] type input
def parse_content(text_list, obj):
    for sent in text_list:
        parsing_help.add_content(sent, obj, language)


def parse_title(title, keywords):
    # wow so parse
    t = title.split()
    for w in t:
        if w.strip('.').lower() in keywords:
            return True
    return False


def parse_threaded(in_doc, in_dir, out_dir, keywords):
    obj = parsed.Parsed()
    with open(in_dir + in_doc, 'r', encoding='utf-8') as jf:
        jsondata = json.load(jf)
        obj.y = parse_date(jsondata['date'])
        obj.url = jsondata['url']
        obj.a = jsondata['author']
        parse_content(jsondata['content']['text'], obj)
        header = jsondata['content']['header'][0]
        if parse_title(header, keywords):
            with open(out_dir + in_doc[:-2] + 'json', 'w', encoding='utf-8') as out:
                out.write(parsing_help.build_json(obj))
                out.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", metavar='in-directory', action="store", help="input directory argument")
    parser.add_argument("-o", help="output directory", action="store")
    parser.add_argument("-lang", help="language", action="store")
    parser.add_argument("-k", help="keywords in title", action="store")

    try:
        args = parser.parse_args()
    except IOError:
        pass

    global language

    if args.i is None:
        common.fail("Please specify input (-i) directory.")
    if args.lang is None:
        language = "english"
    else:
        language = args.lang.lower()

    keywords = set(args.k.split("/"))

    common.build_out(args.o)

    thread_files = []

    for subdir, dirs, files in os.walk(args.i):
        for jf in files:
            if jf[0] != ".":
                thread_files.append((jf, args.i, args.o, keywords))

    pool = Pool()
    pool.starmap(parse_threaded, thread_files)
    pool.close()
    pool.join()

if __name__ == '__main__':
    main()