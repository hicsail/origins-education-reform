# origins-education-reform

A collection of scripts for performing natural language processing tasks on digitized texts.
* ``XMLParsingScript.py -i input_files_folder_path -o output_files_folder_path``

    A script for converting the XML files that conform to the [Text Encoding Initiative (TEI)](http://www.tei-c.org/index.xml) format to a custom JSON format amenable to NLP transformations.
    * ``-i input_files_folder_path``

        Specify filepath to directory containing the input files (required).
    * ``-o output_files_folder_path``

        Specify filepath to output directory (required). The script will create a directory with the name you specify, so make sure the filepath you enter isn't already occupied by a directory of the same name.
    
Example usage:

    python3 XMLParsingScript.py -i /Users/Ketchup/Desktop/Danish_Archive -o /Users/Ketchup/Desktop/Text_Out
    
* ``WordFrequency.py``

    A script for performing a word frequency analysis and plotting the results.
    * ``-i input_files_folder_path``
        
        Specify filepath to director containing the input files(required).
    *``-o output_files_folder_path``
    
        Specify filepath to output file (required). The script will create a .txt file with the name you specify, so make sure the filepath you enter isn't already occupied by a directory of the same name.
        
    * ``-k "list_of_keywords" ``
    
        Specify which keywords you wish to perform a frequency analysis on. Separate unique words by spaces, and words with multiple spellings by "/".
        
    * ``-d "min max" ``
    
        Specify the min and max for which decades you would like the program to run the word count on. Separate each value by a space, and surround with quotes.
        
Example usage:

    python3 WordFrequency.py -i /Users/Ketchup/Desktop/Danish_Json_Corpus -o /Users/Ketchup/Desktop/Word_Frequency -k "test1 test2/test3 test4 test5/test6/test7 test8" -d "1700 1940"

* ``YearScraping.py``
    
    Parses an XML Directory and writes each XML file's Title/Author/Year of publication to a .txt file. It ignores XML documents whose chapter/text fields are empty. We're just using it to simplify the process of assigning years to documents, since the bulk of it will have to be done manually. The I/O is identical to XMLParsingScript.py above.

Rsync Instructions:

    curl -L http://cpanmin.us | perl - —sudo App::cpanminus 
(pkg manager)

    which cpan 
    which cpanm

    sudo cpanm File::Pairtree
(install Pairtree module)
