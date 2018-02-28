#!/bin/bash

cd ../../..

XML_INPUT_DIR=$1
HT_INPUT_DIR=$2
OUTPUT_DIR=$3
WORKING_DIR=$(pwd)

HT_FILE_PATH=$WORKING_DIR'/parsing/HT_Parser.py'
XML_PARSER_PATH=$WORKING_DIR'/parsing/Danish_XML_Parser.py'

HT_CSV_PATH=$WORKING_DIR'/csv_files/danish_csv.csv'
XML_CSV_PATH=$WORKING_DIR'/csv_files/danish_publication_dates.csv'

python3 $HT_FILE_PATH -csv $HT_CSV_PATH -o $OUTPUT_DIR -x $INPUT_DIR  -lang 'danish'

python3 $XML_PARSER_PATH -i $INPUT_DIR -o $OUTPUT_DIR -csv $XML_CSV_PATH