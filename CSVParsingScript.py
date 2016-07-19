import csv, argparse, os, shutil

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", metavar='in-directory', action="store", help="input directory argument")
    parser.add_argument("-o", help="output file argument", action="store")

    try:
        args = parser.parse_args()
    except IOError:
        pass

    if not os.path.exists(args.o):
        os.mkdir(args.o)
    else:
        shutil.rmtree(args.o)
        os.mkdir(args.o)

    for subdir, dirs, files in os.walk(args.i):
        for csvfile in files:
            out = open(args.o + csvfile[:-4] + ".txt", 'w', encoding='utf-8')
            with open(args.i + csvfile, encoding='utf-8') as file:
                readCSV = csv.reader(file, delimiter=',')
                data = {}
                for row in readCSV:
                    if row[0] != "htid":
                        author = row[4]
                        author_cleaned = author.strip(",._-:;\"'\\()[]0123456789!?").lower()
                        #Check if author exists in data
                        if data.get(author_cleaned) is not None:
                            pass
                        else:
                            #Add author to data
                            data[author_cleaned] = {}
                        title = row[10]
                        title_cleaned = title.strip(",._-:;\"'\\()[]0123456789!?").lower()
                        #Check if book title exists in data w/r/t a specific author
                        if data[author_cleaned].get(title_cleaned) is not None:
                            #Book exists already, check for dates
                            pubDate = row[6]
                            pubDate_cleaned = pubDate.strip()[:4]
                            currentDate = [w for w in data[author_cleaned][title_cleaned]]
                            #currentDate = int(currentDate[0])
                            if int(pubDate_cleaned) < int(currentDate[0]):
                                #This date comes earlier, overwrite current date & volume entries
                                del data[author_cleaned][title_cleaned][currentDate[0]]
                                data[author_cleaned][title_cleaned][pubDate_cleaned] = {}
                                #Add volume number
                                volume = row[8]
                                volume_cleaned = volume.replace(" ", "").lower()
                                if volume_cleaned == "":
                                    volume_cleaned = "v.1"
                                htid = row[0]
                                data[author_cleaned][title_cleaned][pubDate_cleaned][volume_cleaned] = htid
                            else:
                                #This date comes after, ignore it
                                pass
                        else:
                            #Book doesn't exist yet, add to data
                            data[author_cleaned][title_cleaned] = {}
                            pubDate = row[6]
                            pubDate_cleaned = pubDate.strip()[:4]
                            data[author_cleaned][title_cleaned][pubDate_cleaned] = {}
                            #Add volume number
                            volume = row[8]
                            volume_cleaned = volume.replace(" ", "").lower()
                            if volume_cleaned == "":
                                volume_cleaned = "v.1"
                            htid = row[0]
                            data[author_cleaned][title_cleaned][pubDate_cleaned][volume_cleaned] = htid
                for author in data:
                    for book in data[author]:
                        for date in data[author][book]:
                            for volume in data[author][book][date]:
                                id = str(data[author][book][date][volume])
                                id = id.replace("+", ":")
                                id = id.replace("=", "/")
                                out.write(id + "\n")

if __name__ == '__main__':
    main()