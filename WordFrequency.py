import json
import os
import nltk
import argparse
import math
import matplotlib.pyplot as plt

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

def buildDict(decades, keywords, results):
    for decade in decades:
        for keyword in keywords:
            try:
                results[decade][keyword] = 0
            except KeyError:
                results[decade] = {keyword: 0}
    return results

def buildDecadeTally(decades, decadeTally):
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
                text = jsondata["9.Filtered Text"]
                year = jsondata["4.Year Published"]
                decade = int(year) - int(year)%10
                try:
                    decadeTally[decade] += 1
                except KeyError:
                    pass
    return decadeTally

def buildTF_IDF(keywords, decades, idfResults, tfResults, tf_idfResults):
    for decade in decades:
        for keyword in keywords:
            tf_idfResults[decade][keyword] += tfResults[decade][keyword] * idfResults[decade][keyword]
    return tf_idfResults

def findMax(keywords, decades, tf_idfResults):
    max = 0
    for decade in decades:
        for keyword in keywords:
            if tf_idfResults[decade][keyword] > max:
                max = tf_idfResults[decade][keyword]
    return max

def tf_idfAvg(decades, keywords, tf_idfResults, decadeTally):
    #Take average of TF_IDF results
    for decade in decades:
        for keyword in keywords:
            try:
                num1 = tf_idfResults[decade][keyword]
                num2 = decadeTally[decade]
                val = round((num1/num2), 4)
                tf_idfResults[decade][keyword] = val
            except ZeroDivisionError:
                tf_idfResults[decade][keyword] = 0
    return tf_idfResults

def calculateTF(fdist, w):
    termFreq = fdist[w]
    maxFreq = fdist[fdist.max()]
    TF = (termFreq/maxFreq)
    return TF


def calculateTFResults(keywords, decades, directory, tfResults):
    for subdir, dirs, files in os.walk(directory):
        for jsondoc in files:
            with open(directory + "/" + jsondoc, 'r') as input:
                jsondata = json.load(input)
                text = jsondata["9.Filtered Text"]
                year = jsondata["4.Year Published"]
                decade = int(year) - int(year)%10
                fdist = nltk.FreqDist(text)
                for keyword in keywords:
                    words = keyword.split("/")
                    temp = 0
                    for w in words:
                        temp += calculateTF(fdist, w)
                    try:
                        tfResults[decade][keyword] += temp
                    except KeyError:
                        pass
    '''
    for decade in decades:
        for keyword in keywords:
            temp = tfResults[decade][keyword]
            new = .5 + (.5 * temp)
            tfResults[decade][keyword] = new
    '''

    return tfResults

def calculateIDFResults(keywords, decades, decadeTally, directory, idfResults):
    for subdir, dirs, files in os.walk(directory):
        for jsondoc in files:
            with open(directory + "/" + jsondoc, 'r') as input:
                jsondata = json.load(input)
                text = jsondata["9.Filtered Text"]
                year = jsondata["4.Year Published"]
                decade = int(year) - int(year)%10
                fdist = nltk.FreqDist(text)
                for keyword in keywords:
                    words = keyword.split("/")
                    for w in words:
                        if fdist[w] > 0:
                            try:
                                idfResults[decade][keyword] += 1
                                break
                            except KeyError:
                                pass
                        else:
                            pass
    for decade in decades:
        for keyword in keywords:
            try:
                #Add 1 before logarithm to ensure idf is nonzero
                #Otherwise, a bunch of the values are zero (b/c log(1))
                #and there's not much data to see
                idfResults[decade][keyword] = \
                    1 + round(math.log(((decadeTally[decade]) / max(1, idfResults[decade][keyword])), 10), 4)
            except KeyError:
                pass
    return idfResults


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

    decadeTally = {}
    tf_idfResults = {}
    tfResults = {}
    idfResults = {}

    decadeTally = buildDecadeTally(decades, decadeTally)
    decadeTally = populateDecadeTally(directory, decadeTally)

    tf_idfResults = buildDict(decades, keywords, tf_idfResults)
    tfResults = buildDict(decades, keywords, tfResults)
    idfResults = buildDict(decades, keywords, idfResults)
    idfResults = calculateIDFResults(keywords, decades, decadeTally, directory, idfResults)
    tfResults = calculateTFResults(keywords, decades, directory, tfResults)
    tf_idfResults = buildTF_IDF(keywords, decades, idfResults, tfResults, tf_idfResults)
    tf_idfResults = tf_idfAvg(decades, keywords, tf_idfResults, decadeTally)

    max = findMax(keywords, decades, tf_idfResults)

    out = open(args.o + ".txt", 'w')

    for decade in decades:
        out.write("Decade: " + str(decade) + "\n")
        out.write("Number of books for this decade: " + str(decadeTally[decade]) + "\n")
        for keyword in keywords:
            out.write(keyword + ":")
            out.write(str(tf_idfResults[decade][keyword]) + "\n")
        out.write("\n")

    for keyword in keywords:
        i = 0
        a = [0]*(len(decades))
        while i < len(decades):
            a[i] += tf_idfResults[decades[i]][keyword]
            i += 1
        plt.plot(decades, a, label=keyword)
    plt.legend(bbox_to_anchor=(0, 1.02, 1., .102), loc=3, ncol=int(len(keywords)/2),
           mode="expand", borderaxespad=0.)
    plt.xlabel("Decade")
    plt.ylabel("Word Frequency")
    plt.axis([int(min_max[0]), int(min_max[1]), 0, max])
    plt.show()

if __name__ == '__main__':
    main()























