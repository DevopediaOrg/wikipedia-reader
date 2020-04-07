import re
import sys
from parsers import WikitextParser, HtmlParser


class ArticleReader:
    ''' Read article content using suitable parsers.
    '''

    def __init__(self, **kwargs):
        self.config = kwargs
        self.wtparser = WikitextParser(**kwargs)
        self.hparser = HtmlParser(**kwargs)

    def get_seed_links(self, text, targets=None):
        return self.wtparser.get_seed_links(text, targets)

    def get_links(self, title, text, html):
        links = self.wtparser.get_links(title, text)

        if self.config['transcludes']['enabled']:
            transcludes = self.wtparser.get_transcludes(text)
            transcludes |= self.hparser.get_transcludes(html)
        else: transcludes = set()

        return links, transcludes
