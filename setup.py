from setuptools import setup

setup(
    name             = 'origins-education-reform',
    version          = '0.0.0.1',
    packages         = ['nlp_scripts',],
    install_requires = ['nltk', 'gensim', 'numpy',],
    license          = 'MIT',
    url              = 'https://github.com/hicsail/origins-education-reform',
    description      = 'NLP scripts',
    long_description = open('README.md').read(),
)
