from PIL import Image
import argparse

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i",
        help="Input directory path",
        action="store",
        required=True
    )
    parser.add_argument(
        "-o",
        help="Output filename",
        action="store",
        required=True
    )

    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()

    im = Image.open(args.i)
    im.save(args.o)