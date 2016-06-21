import json
import os
import nltk
import re
import matplotlib.pyplot as plt

decades = [1800, 1810, 1820, 1830, 1840, 1850, 1860, 1870,
           1880, 1890, 1900, 1910, 1920]


keywords = ["folk", re.compile(r"\bgive\b|\bgiver\b"), "pligt",
            re.compile(r'\brettighed\b|\brettigheder\b'), "domstol",
            "marked"]
results = {}
decadeTally = {}

#Can just build this dynamically (with the try block)
for decade in decades:
    for keyword in keywords:
        try:
            results[decade][keyword] = 0
        except KeyError:
            results[decade] = {keyword: 0}

for decade in decades:
    try:
        decadeTally[decade] = 0
    except KeyError:
        pass
###
#Specify input directory here
###
directory = ""

for subdir, dirs, files in os.walk(directory):
    for jsondoc in files:
        with open(directory + "/" + jsondoc, 'r') as input:
            jsondata = json.load(input)
            text = jsondata["8.Full Text"]
            year = jsondata["4.Year Published"]
            decade = int(year) - int(year)%10
            try:
                decadeTally[decade] += 1
            except KeyError:
                pass
            textList = text.split()
            stripped_text = [word.strip(",._-:;\"\'()0123456789!?") for word in textList]
            fdist = nltk.FreqDist(stripped_text)
            for word in fdist.keys():
                for keyword in keywords:
                    try:
                        if keyword.match(word.lower()):
                            try:
                                results[decade][keyword] += fdist[word]
                            except KeyError:
                                # Word not found in fdist
                                pass
                    except AttributeError:
                        if word.lower() == keyword:
                            try:
                                results[decade][keyword] += fdist[word]
                            except KeyError:
                                # Word not found in fdist
                                pass

for keyword in keywords:
    i = 0
    a = [0]*(len(decades))
    while i < len(decades):
        a[i] += round(results[decades[i]][keyword] / decadeTally[decades[i]], 2)
        i += 1
    print(keyword)
    print(a)

for keyword in keywords:
    i = 0
    a = [0]*(len(decades))
    while i < len(decades):
        a[i] += results[decades[i]][keyword] / decadeTally[decades[i]]
        i += 1
    plt.plot(decades, a, label=keyword)
plt.legend(bbox_to_anchor=(0, 1.02, 1., .102), loc=3, ncol=3,
           mode="expand", borderaxespad=0.)
plt.xlabel("Decade")
plt.ylabel("Word Frequency")
plt.axis([1800, 1920, 0, 85])
plt.show()
