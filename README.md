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

    A script for performing a word frequency analysis.
    
    * ``-i input_files_folder_path``
        
        Specify filepath to director containing the input files(required).
        
    * ``-txt output_file_path``
    
        Specify filepath to output file (required). The script will create a .txt file with the name you specify, so make sure the filepath you enter isn't already occupied by a directory of the same name.
    
    * ``-csv output_file_path``
    
        Specify filepath to output csv file (required). The filepath will be printed in the txt file for each run as well, to so the user can keep track. The csv file created is used as input to GraphCSV.py.
        
    * ``-k "list_of_keywords"``
    
        Specify which keywords you wish to perform a frequency analysis on. Separate unique words by commas. If you would like to count certain words together (e.g. "train" & "trains"), then separate them with a forward slash ("/") character. They will then be treated as the same keyword. Surround the entire list with quotes.
        
    * ``-b ``
        
        Flag that tells the script to search for bigrams rather than individual words. Rules for building a bigram key list are the same as with single keywords, just separate words within a bigram with a whitespace.
        
    * ``-y "min max inc" ``
    
        Specify the min and max for which years you would like the program to run the word count on, as well as the increment value. Separate each value by a space, and surround with quotes.
        
    * ``-p`` 
    
        Boolean flag to control whether the script will be analyzing groups of text according to a fixed increment value (default), or by periods of arbitrary length. This flag controls periods of arbitrary length.
        
    * ``-periods "int1 int2 int3 int4"``
    
        Specifies the begin and end date for each period the user would like to analyze. The periods are exclusive, so the string above instructs the script to look for text from years int1 to (int2 - 1), int2 to (int3 - 1), and so on.
        
    * ``-num "integer" `` 
    
        Tells the script how many top words per decade to display.
    
    * ``-type "text_type"``
    
        Tells the script which field of the Json documents to analyze. For example, if you wanted to analyze a field called "Happy Text" within the Json docs of your corpus, your input would look like -type "Happy Text".
    
Example usage:

    python3 WordFrequency.py -i /Users/Ketchup/Desktop/Danish_Json_Corpus/ -txt /Users/Ketchup/Desktop/Word_Frequency -csv /Users/Ketchup/Desktop/Wordcsv -k "test1 test2/test3 test4 test5/test6/test7 test8" -y "1700 1940 5" 
    
* ``SentBuilder.py``

    A script for parsing a corpus of text and outputting snippets of text surrounding the occurrence of keywords.
    
    * `` -i <filepath to full corpus> ``
    
        Filepath to input directory. The directory itself must be filled with Json files, no subdirectories.
        
    * `` -o <filepath to output directory> ``
    
        Filepath to output directory. 
    * `` -k "list of keywords" ``
    
        List of keywords. The syntax for the argument itself is identical to the scripts above. 
        
    * `` -b ``
    
        Controls whether your list of keywords is interpreted as a list of bigrams or individual keywords.
        
    * `` -len "integer" ``
    
        Number of words around each occurence of a keyword to extract.
        
    * `` -type "text_type" ``
    
        Indicates which subfield of each Json document you'd like to parse. For example, our current corpus has four sub-fields: "Full Text", "Filtered Text", "Full Text Stemmed", and "Filtered Text Stemmed". 
        
    * `` -y "min_year max_year" ``
    
        Range of years you'd like to include.
        
* ``SentAnalysis.py``

    A script for parsing the output of SentBuilder.py and returning sentiment scores for text around keywords over time. The input directory is required to be of the same structure as the output of SentBuilder.py, i.e. - the filepath to the top level directory is the input directory ( `` -i ``), and within it there are subdirectories corresponding to each keyword that you'd like to to analyze. The other input arguments are used as follows:
    
    * `` -c <full corpus file path> ``
    
        This is the filepath to the full corpus which corresponds to the text being analyzed (i.e. - the corpus used to build the text you're analyzing). Unlike the directory structure for the input directory described above, this directory structure must be a single top level directory filled with Json documents. 
        
    * `` -y "min_year max_year increment" OR -y "period_1 period_2 period_3 ... period_n" ``
    
        If you're looking at a range of years with a fixed increment value (e.g. - by decades), use the first structure. If you'd like periods of arbitrary length, use the second. Note that if using the second, you must use the periods flag (`` -p ``) on the command line, or the script won't know what to do with it.
        
    * `` -num "integer" ``
    
        This tells the script how many maximum/minimum documents to output from each period in the text file at the end of the run. Knowing the documents with the highest and lowest sentiment scores can be useful for understanding whether certain results are being caused by several outliers or truly representative of the corpus itself.
        
    * `` -language "en/da" ``
    
        Indicates which language your corpus is in. Note that 'en' is for English, while 'da' is for Danish.
        
    * `` -csv <filepath to output CSV file> ``
    
        Filepath to outputted CSV file. This file can be passed to GraphCSV.py to plot data from the run.
        
    * `` -txt <filepath to output txt file> ``
    
        Filepath to outputted text file. This file contains more specific information about the run.


* ``GraphCSV.py``

    Reads from CSV files and produces graphs representing the statistics stored in them. Can produce either line graphs or bar graphs.
    
        * If you are graphing output from the script SentAnalysis.py, use the flag `` -sa `` anywhere on the command line. If you are using output from the script WordFrequency.py, type `` -wf `` on the command line.

        * The following five flags determine which of the collected data is represented on a graph & how that data is represented. If -bar is not entered, the graph will be a line graph by default. At least one of the bottom four flags must be selected. 
      
        * ``-bar``
        
            The script will generate a line graph by default, but setting this flag will cause it to output a bar graph instead.
        
        * ``-t_avg``
        
            Graph the average tfidf score for each keyword/decade pair.
            
        * ``-t_max`` 
        
            Graph the max tfidf score for each keyword/decade pair.
            
        * ``-t_min`` 
        
            Graph  the min tfidf score for each keyword/decade pair.
            
        * ``-percent``
        
            Graph basic term frequency as a percentage of total words for each decade.
            
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

### Centos 7 Installation:
Run the following commands on a clean Centos 7 server on the MOC.
```
$ sudo yum -y update && sudo yum -y groupinstall development && sudo yum -y install vim openssl-devel bzip2-devel readline-devel sqlite-devel
$ curl -L https://raw.githubusercontent.com/yyuu/pyenv-installer/master/bin/pyenv-installer | bash
$ source ~/.bash_profile
$ pyenv install 3.5.2
```
