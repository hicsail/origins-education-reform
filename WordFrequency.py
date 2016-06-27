
import json
import os
import nltk
import argparse

def buildKeyList(keywords):
    keyList = keywords.split()
    return keyList

def buildDecadesList(min, max):
    decadesMin = int(min)
    decadesMax = int(max)
    numElements = ((decadesMax - decadesMin) / 10)
    decades = [None] * int(numElements)
    i = 0
    for num in range(decadesMin, decadesMax, 10):
        decades[i] = num
        i += 1
    return sorted(decades)

def buildDict(decades, keywords):
    results = {}
    for decade in decades:
        for keyword in keywords:
            try:
                results[decade][keyword] = 0
            except KeyError:
                results[decade] = {keyword: 0}
    return results

def buildDecadeTally(decades):
    decadeTally = {}
    for decade in decades:
        try:
            decadeTally[decade] = 0
        except KeyError:
            pass
    return decadeTally

def populateDecadeTally(directory, decadeTally):
    for subdir, dirs, files in os.walk(directory):
        for jsondoc in files:
            with open(directory + "/" + jsondoc, 'r') as input:
                jsondata = json.load(input)
                text = jsondata["8.Full Text"]
                year = jsondata["4.Year Published"]
                decade = int(year) - int(year)%10
                if text == "":
                    pass
                else:
                    try:
                        decadeTally[decade] += 1
                    except KeyError:
                        pass
    return decadeTally

def buildFreqDist(directory, keywords, results):
    for subdir, dirs, files in os.walk(directory):
        for jsondoc in files:
            with open(directory + "/" + jsondoc, 'r') as input:
                jsondata = json.load(input)
                text = jsondata["8.Full Text"]
                year = jsondata["4.Year Published"]
                decade = int(year) - int(year)%10
                textList = text.split()
                stripped_text = [word.strip(",._-:;\"\'()0123456789!?") for word in textList]
                cleaned_text = [word.lower() for word in stripped_text]
                if text == "":
                    pass
                else:
                    fdist = nltk.FreqDist(cleaned_text)
                    for keyword in keywords:
                        words = keyword.split("/")
                        for w in words:
                            try:
                                num = fdist[w]
                                results[decade][keyword] += num
                            except KeyError:
                                pass
    return results

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", metavar='in-directory', action="store", help="input directory argument")
    parser.add_argument("-o", help="output file argument", action="store")
    parser.add_argument("-k", help="list of keywords argument, surround list with quotes", action="store")
    parser.add_argument("-d", help="min/max for decades list, surround with quotes", action="store")

    try:
        args = parser.parse_args()
    except IOError:
        pass

    directory = args.i
    keywords = buildKeyList(args.k)
    min_max = args.d.split()
    decades = buildDecadesList(min_max[0], min_max[1])

    results = buildDict(decades, keywords)
    results = buildFreqDist(directory, keywords, results)

    decadeTally = buildDecadeTally(decades)
    populateDecadeTally(directory, decadeTally)

    out = open(args.o + ".txt", 'w')

    for decade in decades:
        out.write("Decade: " + str(decade) + "\n")
        out.write("Number of books for this decade: " + str(decadeTally[decade]) + "\n")
        for keyword in keywords:
            out.write(keyword + ":")
            out.write(str(results[decade][keyword]) + "\n")
        out.write("\n")

if __name__ == '__main__':
    main()
