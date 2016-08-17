# origins-education-reform

A collection of scripts for performing natural language processing tasks on digitized texts.
* ``XMLParsingScript.py -i input_files_folder_path -o output_files_folder_path``

    A script for converting the XML files that conform to the [Text Encoding Initiative (TEI)](http://www.tei-c.org/index.xml) format to a custom JSON format amenable to NLP transformations.
    * ``-i input_files_folder_path``

        Specify filepath to directory containing the input files (required).
    * ``-o output_files_folder_path``

        Specify filepath to output directory (required). The script will create a directory with the name you specify, so make sure the filepath you enter isn't already occupied by a directory of the same name.
    *"-f"
        
        Filter the raw text by removing stop-words and unnecessary characters, returning an array of individual words in each Json file. Note that if you specify the filtering argument, the script will take ~1 hour to run.
    
Example usage:

    python3 XMLParsingScript.py -i /Users/Ketchup/Desktop/Danish_Archive/ -o /Users/Ketchup/Desktop/Text_Out/
    
* ``WordFrequency.py``

    A script for performing a word frequency analysis and plotting the results.
    * ``-i input_files_folder_path``
        
        Specify filepath to director containing the input files(required).
        
    * ``-o output_file_path``
    
        Specify filepath to output file (required). The script will create a .txt file with the name you specify, so make sure the filepath you enter isn't already occupied by a directory of the same name.
        
    * ``-k "list_of_keywords"``
    
        Specify which keywords you wish to perform a frequency analysis on. Separate unique words by spaces. If you would like to count certain words together (e.g. "train" & "trains"), then separate them with a forward slash ("/") character. They will then be treated as the same keyword. Surround the entire list with quotes.
        
    * ``-d "min max" ``
    
        Specify the min and max for which decades you would like the program to run the word count on. Separate each value by a space, and surround with quotes.
        
    * ``-n``
    
        Boolean flag that controls whether the script will search for the top word frequencies per decade. The results of the search are then printed onto a text file when the script finishes running.
        
    * ``-num "integer" `` 
    
        If the flag ``-n`` above is selected, this field is also required. It tells the script how many top words per decade to look for.
        
    * The following four flags determine which of the collected data is represented on a graph. While only one may be selected,
      all of them are written to a text file when the script finishes running. If none are selected, then nothing will be graphed and none of them will be written to the text file.
        
        * ``-t_avg``
        
            Graph the average tfidf score for each keyword/decade pair.
            
        * ``-t_max`` 
        
            Graph the max tfidf score for each keyword/decade pair.
            
        * ``-t_min`` 
        
            Graph  the min tfidf score for each keyword/decade pair.
            
        * ``-percent``
        
            Graph basic term frequency as a percentage of total words for each decade.
    
Example usage:

    python3 WordFrequency.py -i /Users/Ketchup/Desktop/Danish_Json_Corpus/ -o /Users/Ketchup/Desktop/Word_Frequency -k "test1 test2/test3 test4 test5/test6/test7 test8" -d "1700 1940" -percent

* ``YearScraping.py``
    
    Parses an XML Directory and writes each XML file's Title/Author/Year of publication to a .txt file. It ignores XML documents whose chapter/text fields are empty. We're just using it to simplify the process of assigning years to documents, since the bulk of it will have to be done manually. The I/O is identical to XMLParsingScript.py above.

* ``HT_Parsing.py``

    Navigates the HT directories and extracts .txt files and their corresponding HTIDs. Then pairs each HTID with it's corresponding row in the HT CSV files and builds a Json file similar to those created by XMLParsingScript.py above.
    *``-i input_files_folder_path``
    
        Specify folder containing the HT directories/files (required).
        
    *``-o output_files_folder_path``
    
        Specify filepath to output directory (required). If the directory already exists, it will be overwritten.
        
    *``-c csv_file_path``
    
        Specify path to the CSV file you will be using to populate each Json file's Author, Title, PubInfo, and Year fields. (required)
        Make absolutely sure that the CSV file is UTF-8 encoded, or the script will fail. If you do not know which encoding your CSV
        file uses, then open it with Notepad++ or SublimeText (or some text editor that lets you change encodings) and switch the 
        encoding of the file to UTF-8.

### Rsync Instructions:

Install Pairtree for Perl:

```
$ curl -L http://cpanmin.us | perl - —sudo App::cpanminus 

which cpan 
which cpanm

sudo cpanm File::Pairtree
```

Run this [rsync script](https://gist.github.com/lit-cs-sysadmin/8ffb90911697adc1262c) on SCC1.bu.edu. Use ht_text_pd as the $TREE value.
