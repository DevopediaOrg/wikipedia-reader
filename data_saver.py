import bz2
import json
from glob import glob
import os
import os.path
import re


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
    def write_content_file(cls, fname, content):
        # Derive the next filename suffix
        acfiles = glob(fname + '*.json')
        if acfiles:
            nextid = 1 + max(int(re.sub(r'.*\.(\d+)\.json$', r'\1', os.path.basename(f))) for f in acfiles)
        else:
            nextid = 0
        fname = "{}.{}.json".format(fname, nextid)

        # Save json; read from json and save to bz2
        with open(fname, 'w+', newline='', encoding='utf-8') as jsonfile, \
             bz2.open(fname + '.bz2', 'wb') as bzfile:
            json.dump(content, jsonfile, indent=2)
            jsonfile.seek(os.SEEK_SET)
            bzfile.write(jsonfile.read().encode('utf-8'))


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

