import argparse
import tqdm
import os
import json

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i",
        action="store",
        help="Input directory path",
        required=True
    )
    parser.add_argument(
        "-t",
        help="Text field to use in analysis",
        action="store",
        required=True
    )

    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()

    c = 0
    for _, _, files in os.walk(args.i):
        for jsondoc in tqdm.tqdm(files):
            if jsondoc[0] == ".":
                continue
            with open(f"{args.i}/{jsondoc}", 'r', encoding='utf8') as inpt:
                jsondata = json.load(inpt)
                c += len(jsondata[args.t])

    print(f"Number of words in corpus: {c}")
