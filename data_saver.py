import bz2
import json
from glob import glob
import os
import os.path
import re


class TextSaver:
    ''' Read and write text to file.
    '''

    def __init__(self):
        pass

    @classmethod
    def read_file(cls, fname):
        with open(fname, 'r', encoding='utf-8') as infile:
            return infile.read().strip()

    @classmethod
    def write_file(cls, fname, text):
        with open(fname, "w", encoding='utf-8') as outfile:
            outfile.write(text)


class ArticleSaver:
    ''' Read and write content of one or more articles to disk.
    Articles are saved in JSON format.
    '''

    def __init__(self):
        pass

    @classmethod
    def read_content_file(cls, fname):
        content = []
        try:
            with open(fname, 'r', encoding='utf-8') as jsonfile:
                content = json.load(jsonfile)
        except FileNotFoundError:
            pass
        return content

    @classmethod
    def write_content_file(cls, prefix, content):
        # Derive the next filename suffix
        acfiles = glob(prefix + '*.bz2')
        if acfiles:
            nextid = 1 + max(int(re.sub(r'.*\.(\d+)\.json\.bz2$', r'\1', os.path.basename(f))) for f in acfiles)
        else:
            nextid = 1 # start from 1, not 0
        fname = "{}.{}.json.bz2".format(prefix, nextid)

        # Unzip on Linux: bzip2 -dk *.bz2
        with bz2.open(fname, 'wb') as bzfile:
            bzfile.write(json.dumps(content, indent=2).encode('utf-8'))


class TitleSaver:
    ''' Read and write article titles to disk in text format.
    Each line has one title.
    '''

    def __init__(self):
        pass

    @classmethod
    def read_title_file(cls, fname):
        try:
            with open(fname, 'r', encoding='utf-8') as infile:
                titles = set([line.strip() for line in infile.readlines()])
        except FileNotFoundError:
            titles = set()
        return titles

    @classmethod
    def write_title_file(cls, fname, titles):
        with open(fname, "w", encoding='utf-8') as outfile:
            for t in titles:
                outfile.write(t + "\n")

