#!/bin/bash

INPUT_DIR=$1
OUTPUT_DIR=$2
WORKING_DIR=$(pwd)

HT_FILE_PATH=$WORKING_DIR'/parsing/HT_Parser.py'
CSV_DIR=$WORKING_DIR'/csv_files/british_csv.csv'

python3 $HT_FILE_PATH -csv $CSV_DIR -o $OUTPUT_DIR -x $INPUT_DIR  -lang 'english'