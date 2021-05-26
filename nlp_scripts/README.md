## Data Formats

### Corpora

A corpus is a folder of `.json` files. Each `.json` file represents a text, e.g. a book. The `.json` file contains information about the text, e.g. its author and its country of origin. It also includes words from the text in various forms of processing. 

### Graph Input

The graphing scripts take a folder of `.json` files as input. Each `.json` file represents a corpus that has been processed through `WordFrequency.py`.  

## Scripts

### WordFrequency.py

Computes statistics of various words in a corpus, e.g. TF-IDF, the most times the words appear in a text, etc. 

Command line arguments:
| Argument							| Required? | Explanation 						|
| :--								| :--		| :--								|
| `-i [path]` 						| Yes		| Path to input corpus directory	|
| `-k "[word] [word]..."` 			| Yes		| Words used for analysis			|
| `-y "[start] [end] [increment]"` 	| Yes		| Output year buckets				|
| `-txt [name]` 					| Yes		| Text output filename				|
| `-json [name]` 					| Yes		| JSON output filename				|
| `-type [field]` 					| No		| Path to input corpus directory	|
| `-nat [nation]` 					| No		| The corpus's nation for graphing	|
| `-b` 								| No		| Set to analyse bigrams			|
| `-num [num]` 						| No		| Find the `num` most common words	|

### graphing.py

Produces a graph to compare various metrics across different corpora. 

Command line arguments:
| Argument						| Required? | Explanation 							|
| :--							| :--		| :--									|
| `-i [path]` 					| Yes		| Path to input corpus directory		|
| `-o [path]` 					| No		| Filename for graph output				|
| `-bar` 						| No		| Creates a bar instead of line graph 	|
| `-b_width [num]` 				| No		| Sets a bar graph's bar widths			|
| `-yaxis "[num] [num]"` 		| No		| Sets y-axis limits					|
| `-padding [num]` 				| No		| Sets the padding on the graph's edges	|
| `-leg [num]` 					| No		| Sets the legend size					|
| `-titlesize [num]` 			| No		| Sets the title size in pt				|
| `-labelsize [num]` 			| No		| Sets the data label size in pt		|
| `-axislabelsize [num]` 		| No		| Sets the axis label size in pt		|
| `-breakdown` 					| No		| Graphs the statistics by word			|

In addition, one of the following command line arguments is required to decide what statistic to graph:
| Argument		| Explanation 											|
| :--			| :--													|
| `-avg` 		| Average TF-IDF										|
| `-max` 		| Maximum TF-IDF										|
| `-min` 		| Minimum TF-IDF										|
| `-percent` 	| Word frequency as a percentage of words in the corpus |
| `-mean` 		| Average word frequency in texts						|
| `-var` 		| Variance of word frequencies in textx					|

### world_politics_graph.py

Produces a graph to compare various metrics across different corpora.

Command line arguments:

See graphing.py