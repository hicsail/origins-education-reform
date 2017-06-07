### Author: Justin Chen
#### 5.20.17

### Requirements
- Python 3
- BeautifulSoup 4
- urllib
- multiprocessing
- datetime

### Basic usage
```
$ python parliament.py --save my_data
```
This will scrape the Hansard Parliament website for all sittings starting from 1802-07-02 (July 2nd, 1802) to 2006-0424 (April 24th, 2006) and save all the data in the directory my_data. If the directory does not exist, the script will create it.

#### Search by date range
```
$ python parliament.py --start_year 1803 --start_month 11 --start_day 22 --end_year 1803 --end_month 12 --end_day 20
```
If you just want to search for all sittings in a specific year without specifying a particular month and day, just set `--end_month 12` and `end_day 31`.

#### Resume search
If you need to resume the search, use the `--resume` flag, which will load the available data from the `save` directory and determine which files are missing and where to resume the search. This flag can also be used in conjunction with the date flags to resume and stop at a specified date. This assumes all the files from the previous run exist in `save`.
```
$ python parliament.py --resume True
```

#### Parallelize
The Hansard website seems to get easily overwheelmed, so specify a narrow date range when using this flag to avoid having to resume.
```
$ python parliament.py --parallel True --start_year 1803 --start_month 11 --start_day 22 --end_year 1803 --end_month 12 --end_day 20
```

#### Example sitting output
All sittings are saved in JSON files and are named using the convention year-month-day-sitting_title.js. For example:
```
1803-11-23-boston_election_fetitiom.js

{'author': 'UK Parliament',
 'content': {'header': ['BOSTON ELECTION FETITIOM.\\u2014',
                        'HC Deb 23 November 1803 vol 1 cc32-3'],
             'text': ['Mr. Ellison\n\n            adverted to the petition of John Ogle, Esq. complaing of an undue election and return for the borough of Boston, in the county of Lincoln, against Mr. Fydell, the present sitting member. He desired that the entry on the journals respecting this petition, might be read; which was accordingly done. He then desired that an entry on the journals in the year 1744, relative to the case of a petitioner who had been allowed seven days time to give in his qualification, on account of his being beyond seas at the time he was served with notice to do so, which he said was precisely the case of the present sitting member, Mr. Fydell; which entry being read, he moved, "that Mr. Fydell be allowed seven days from this present day, in order to prepare and lay before the house, a particular account of his qualification to be admitted as a member."\n          \n\n\n33',
                      "The Speaker\n\n            entered into a foil explanation of the case. He reminded the house of the jealousy with which they were always actuated in matters of this nature. Yet he was well aware that laudable as that jealousy was, it would never stand in the way of justice and equity when they could be fairly attended without prejudice to either party. It was determined, by an order of the house, that when the qualification of candidates was called in question, the particulars of that qualification should be produced by him within fifteen days after the complaint of his wanting it, was made against him. The usual notice, it appears, had been sent to Mr. Fydell, in the present case, but not complied with; and the reason adduced for his non-compliance was his indispensible absence beyond sea. A precedent, similar to the present case, occured in the year 1744. It respected also a naval officer who was necessarily absent on the service of his country; and the house then judged it fit to extend the time. Should the house be now inclined to grant the same indulgence, they would agree to the motion made by the honourable gent.\\u2014Mr. Ellison's motion was then put and agreed to."]},
 'date': '1803-11-23',
 'url': 'http://hansard.millbanksystems.com/commons/1803/nov/23/boston-election-fetitiom'}
```
***Note: When loading this data, should parse it for newlines, tabs, and white spaces as appropriate for your use. There are some odd sittings such as [1803-12-20-commons-preamble](http://hansard.millbanksystems.com/commons/1803/dec/20/preamble)

### Directory structure
```
- parliament
	- parliament.py
	- save
		- api
		- chkpt
			- sittings
			- timeline_urls.p
		- sittings

```

#### save/api directory
This directory contains the JSON from Hansard's API. Files were named by date e.g. 1802-07-02.js (year-month-day). This contains the meta data for the sitting on the given date.
```
1802-07-02.js

[{'house_of_commons_sitting': {'chairman': null,
                               'data_file_id': 52,
                               'date_text': 'Tuesday, July 2.',
                               'end_column': '720',
                               'id': 48,
                               'start_column': '718',
                               'title': 'HOUSE OF COMMONS.',
                               'top_level_sections': [{'section': {'date': '1802-07-02',
                                                                   'end_column': '719',
                                                                   'id': 196,
                                                                   'parent_section_id': 195,
                                                                   'sitting_id': 48,
                                                                   'slug': 'minutes',
                                                                   'start_column': '718',
                                                                   'title': 'Minutes.'}},
                                                      {'section': {'date': '1802-07-02',
                                                                   'end_column': '720',
                                                                   'id': 197,
                                                                   'parent_section_id': 195,
                                                                   'sitting_id': 48,
                                                                   'slug': 'trotters-indemnity-bill',
                                                                   'start_column': '719',
                                                                   'title': "TROTTER'S INDEMNITY BILL."}},
                                                      {'section': {'date': '1802-07-02',
                                                                   'end_column': '720',
                                                                   'id': 198,
                                                                   'parent_section_id': 195,
                                                                   'sitting_id': 48,
                                                                   'slug': 'duke-of-atholls-claim',
                                                                   'start_column': '720',
                                                                   'title': "DUKE OF ATHOLL'S CLAIM."}}],
                               'volume_id': 4,
                               'year': 1802}}]
```

#### save/chkpt/sittings directory
This directory contains the checkpointing information for resuming the script. Each file is named by date e.g. 1802-07-02.js (year-month-day). Each file only contains the titles of all sittings on the given date and the partial URL to that sitting. For example, the DUKE OF ATHOLL'S CLAIM sitting is at http://hansard.millbanksystems.com/commons/1802/jul/02/duke-of-atholls-claim. These files must exist in this location to resume the script from where it left off.
```
1802-07-02.js

{"DUKE OF ATHOLL'S CLAIM.": '/commons/1802/jul/02/duke-of-atholls-claim',
 'Minutes.': '/commons/1802/jul/02/minutes',
 "TROTTER'S INDEMNITY BILL.": '/commons/1802/jul/02/trotters-indemnity-bill'}

```

#### save/chkpt/timeline_url.p
`timeline_url.p` is a pickle file containg all the brute force generated dates for searching a range of dates. This file must exist in this location to resume the script from where it left off.
