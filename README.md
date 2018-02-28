# origins-education-reform

Library for calculating NLP metrics across large corpora. 

## Building Corpora

### British Corpus

Assuming that you have already downloaded the raw data from HathiTrust (paths for British 
corpus located at `/ht_path_lists/british_paths.txt`), run `british_build.sh` (located in this 
directory) as follows:

```
bash british_build.sh <PATH_TO_HT_FILES> <OUTPUT_DIRECTORY_PATH>
```

### Danish Corpus

The Danish corpus is sourced from both HathiTrust and the Danish government. For the HathiTrust files, 
download the raw data exactly as before with the British corpus, but using the path list located at 
`/ht_path_lists/danish_paths.txt`. The non-HathiTrust files are publicly available (TODO - update where
to download). To build the corpus, run `danish_build.sh` (located in this directory) as follows:

```
bash danish_build.sh <PATH_TO_XML_FILES> <PATH_TO_HT_FILES> <OUTPUT_DIRECTORY_PATH>
```

## Downloading HathiTrust data

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
