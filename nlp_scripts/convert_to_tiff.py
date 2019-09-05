from PIL import Image
import argparse

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("-i", help="input file", action="store")
    parser.add_argument("-o", help="output file", action="store")

    args = parser.parse_args()

    im = Image.open(args.i)

    im.save(args.o)