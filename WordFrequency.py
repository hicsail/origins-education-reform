import json
import os
import nltk
import matplotlib.pyplot as plt

decades = [1800, 1810, 1820, 1830, 1840, 1850, 1860, 1870,
           1880, 1890, 1900, 1910, 1920]
keywords = ["folk", "giver", "give", "pligt", "rettighed", "rettigheder",
            "domstol", "marked"]
results = {}

#Can just build this dynamically (with the try block)
for decade in decades:
    for keyword in keywords:
        try:
            results[decade][keyword] = 0
        except KeyError:
            results[decade] = {keyword: 0}

#Enter here where your Danish Json files are located
directory = ""

for subdir, dirs, files in os.walk(directory):
    for jsondoc in files:
        with open(directory + "/" + jsondoc, 'r') as input:
            jsondata = json.load(input)
            text = jsondata["8.Full Text"].split()
            year = jsondata["4.Year Published"]
            decade = int(year) - int(year)%10
            stripped_text = [word.strip(",.\"\':;()0123456789!?") for word in text]
            fdist = nltk.FreqDist(stripped_text)
            for word in fdist.keys():
                for keyword in keywords:
                    if word.lower() == keyword:
                        try:
                            results[decade][keyword] += 1
                        except KeyError:
                            results[decade] = {keyword: 1}

for keyword in keywords:
    i = 0
    a = [0]*(len(decades))
    while i < len(decades):
        a[i] += results[decades[i]][keyword]
        i += 1
    plt.plot(decades, a, label=keyword)

plt.xlabel("Decade")
plt.ylabel("Word Frequency")
plt.axis([1800, 1920, 0, 50])

plt.show()
