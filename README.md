# origins-education-reform

A collection of scripts for performing natural language processing tasks on digitized texts.
* ``XMLParsingScript.py -i input_files_folder_path -o output_files_folder_path``

    A script for converting the XML files that conform to the [Text Encoding Initiative (TEI)](http://www.tei-c.org/index.xml) format to a custom JSON format amenable to NLP transformations.
    * ``-i input_files_folder_path``

        Specify filepath to directory containing the input files (required).
    * ``-o input_files_folder_path``

        Specify filepath to output directory (required). The script will create a directory with the name you specify, so make sure the filepath you enter isn't already occupied by a directory of the same name.
* ``WordFrequency.py``

    A script for performing a word frequency analysis and plotting the results.

Example usage:

    python3 XMLParsingScript.py -i /Users/Ketchup/Desktop/Danish_Archive -o /Users/Ketchup/Desktop/Text_Out
