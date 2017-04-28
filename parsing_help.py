import json, os, re
from nltk.stem.snowball import SnowballStemmer
from nltk.corpus import stopwords


# gathers all info from parsing functions and builds
# a JSON file. also cleans up the file a little bit,
# and checks if some fields are empty.
def build_json(file):
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
    if file.h is None:
        file.h = "No HTID for this file"
    file.t = file.t.replace("\n", " ")
    file.a = file.a.replace("\n", " ")
    file.p = file.p.replace("\n", " ")
    file.d = file.d.replace("\n", " ")
    file.ch = filter_chapters(file.ch)
    jfile = json.dumps({'Title': file.t, 'Author': file.a, 'Publisher': file.p, 'Year Published': file.y,
                        'ISBN': file.i, 'Document Type': file.d, 'List of chapters': file.ch, 'HTID': file.h,
                        'Full Text': file.c, 'Full Text Stemmed': file.cstem, 'Filtered Text': file.tx,
                        'Filtered Text Stemmed': file.txstem, 'Full Sentences': file.c_sent,
                        'Filtered Sentences': file.tx_sent, 'Stemmed Sentences': file.cstem_sent,
                        'Filtered Stemmed Sentences': file.txstem_sent},
                       sort_keys=True, indent=4, separators=(',', ': '), ensure_ascii=False)
    return jfile


# cleans up the chapter list by getting rid of 'None' and empty entries
def filter_chapters(chapters):
    ch = chapters.split(",")
    for i in range(len(ch) - 1, -1, -1):
        if ch[i].strip() == "" or ch[i] is None:
            del ch[i]
    ch_string = ", ".join(ch)
    return ch_string


# helper function to write to a file object. if you want to add more fields
# (lemmatization, etc.) to a Parsed object, you just need to define it in the
# class definition above, write the method(s) for building it, and add it to
# this method along with the build_json method above.
def add_content(text, file, language):
    sentences = re.split('(?<=[.!?]) +', text)
    for sentence in sentences:
        sentence = clean_text(sentence)
        if len(sentence) > 1:
            file.add_content_sent(" ".join(sentence))
            sentence_stemmed = stem_text(sentence, language)
            file.add_stemmed_sent(" ".join(sentence_stemmed))
            sentence_filtered = filter_text(sentence, language)
            if len(sentence_filtered) > 1:
                file.add_filtered_sent(" ".join(sentence_filtered))
                sentence_filtered_stemmed = stem_text(sentence_filtered, language)
                file.add_filtered_stemmed_sent(" ".join(sentence_filtered_stemmed))
    text_list = clean_text(text)
    # full text
    file.add_content(text_list)
    # stem the full text
    stemmed = stem_text(text_list, language)
    file.add_stemmed(stemmed)
    # filter the unstemmed full text
    filtered = filter_text(text_list, language)
    file.add_filtered(filtered)
    # stem the filtered text
    filtered_stemmed = stem_text(filtered, language)
    file.add_filtered_stemmed(filtered_stemmed)


# helper function to write to a file object, same as above but for xml parsing
def add_xml_content(root, file, language):
    text = str(root.text) + str(root.tail)
    sentences = re.split('(?<=[.!?]) +', text)
    for sentence in sentences:
        sentence = clean_text(sentence)
        if len(sentence) > 1:
            file.add_content_sent(" ".join(sentence))
            sentence_stemmed = stem_text(sentence, language)
            file.add_stemmed_sent(" ".join(sentence_stemmed))
            sentence_filtered = filter_text(sentence, language)
            if len(sentence_filtered) > 1:
                file.add_filtered_sent(" ".join(sentence_filtered))
                sentence_filtered_stemmed = stem_text(sentence_filtered, language)
                file.add_filtered_stemmed_sent(" ".join(sentence_filtered_stemmed))
    text_list = clean_text(text)
    # full text
    file.add_content(text_list)
    # stem the full text
    stemmed = stem_text(text_list, language)
    file.add_stemmed(stemmed)
    # filter the unstemmed full text
    filtered = filter_text(text_list, language)
    file.add_filtered(filtered)
    # stem the filtered text
    filtered_stemmed = stem_text(filtered, language)
    file.add_filtered_stemmed(filtered_stemmed)


# converts all letters to lowercase, removes non-alphabetic characters, removes empty strings
def clean_text(text):
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
def filter_text(text_list, language):
    filtered_words = set(stopwords.words(language))
    # Loop backwards because delete changes index
    for i in range(len(text_list) - 1, -1, -1):
        # Delete empty strings or stopwords
        if text_list[i] in filtered_words:
            del text_list[i]
    return text_list


# soop through filtered text and stem all the words
def stem_text(text_list, language):
    # init stemmer & array to store stemmed words
    stemmer = SnowballStemmer(language)
    stemmed = []
    for word in text_list:
        stemmed.append(stemmer.stem(word))
    return stemmed
