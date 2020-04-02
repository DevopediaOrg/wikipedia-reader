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

    def get_links(self, text):
        # Links are within [[]], remove targets
        return set(re.findall(r'\[\[([^#|\]]+)[#\|]?.*?\]\]', text))

    def read_html(self, title, html):
        pass
    