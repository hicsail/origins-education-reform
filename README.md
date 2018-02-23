# origins-education-reform

Library for performing various NLP techniques across corpora. 


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
