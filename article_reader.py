import re


class ArticleReader:
    ''' Given article text, read the raw text and extract
    relevant information. Text is the source text in
    Wikitext syntax. It's not HTML text displayed on a web
    browsers. Wikitext syntax is documented at
    https://en.wikipedia.org/wiki/Help:Cheatsheet
    '''

    def __init__(self, options=None):
        self.options = options

    def read(self, title, text):
        # Links are within [[]], remove targets
        links = re.findall(r'\[\[([^#|\]]+)[#\|]?.*?\]\]', text)
        return (title, text), set(links)
    