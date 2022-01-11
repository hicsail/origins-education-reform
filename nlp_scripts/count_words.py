import argparse
import tqdm
import os
import json


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", action="store", help="input directory argument")
    parser.add_argument("-t", action="store", help="text field to count from")

    args = parser.parse_args()
    input_dir = args.i
    text_field = args.t

    c = 0
    for subdir, dirs, files in os.walk(input_dir):
        for jsondoc in tqdm.tqdm(files):
            if jsondoc[0] == ".":
                continue
            with open(f"{input_dir}/{jsondoc}", 'r', encoding='utf8') as inpt:
                jsondata = json.load(inpt)
                c += len(jsondata[text_field])

    print(f"Number of words in corpus: {c}")
