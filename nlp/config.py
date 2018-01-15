"""
Config classes for NLP scripts
"""
import json


class DeprecatedConfig:

    def __init__(self, i, txt, json, k, y, num, p, b=False, text_type='Words'):
        self.i = i
        self.txt = txt
        self.json = json
        self.b = b
        self.k = k
        self.y = y
        self.num = num
        self.p = p
        self.text_type = text_type


class Config:

    def __init__(self, i):
        self.input_path = i


class WordFrequencyConfig(Config):

    def __init__(self, i):
        super(WordFrequencyConfig, self).__init__(i)
        with open(i, 'r', encoding='utf8') as jc:
            cfg = json.load(jc)
            self.corpus_path = cfg['Paths']['Path to corpus']
            self.text_path = cfg['Paths']['Output text file path']
            self.json_path = cfg['Paths']['Output json file path']

            self.bigrams = cfg['Booleans']['Bigrams']
            self.period = cfg['Booleans']['Periods']

            self.key_list = self._build_key_list(cfg['Parameters']['Keywords'])
            self.year_list = cfg['Parameters']['Year list']
            self.num = cfg['Parameters']['Top words [num]']
            self.type = cfg['Parameters']['Type']

    def _build_key_list(self, keys):
        key_list = keys.lower().split(",")
        key_list = [keyword.strip() for keyword in key_list]
        if self.bigrams:
            bigram_list = []
            key_list = [tuple(keyword.split("/")) for keyword in key_list]
            for i in range(len(key_list)):
                temp_list = list(key_list[i])
                temp_list = [tuple(elem.split()) for elem in temp_list]
                temp_list = tuple(temp_list)
                bigram_list.append(temp_list)
            return bigram_list
        return key_list

