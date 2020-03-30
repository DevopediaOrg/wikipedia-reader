import re


class ArticleReader:
    ''' Given article text, read the raw text and extract
    relevant information. Text is the source text in
    Wikitext syntax. It's not HTML text displayed on a web
    browsers.  
    '''

    def __init__(self, options=None):
        self.options = options

    def read(self, title, text):
        links = re.findall(r'\[\[([^|\]]+)\|?.*?\]\]', text)
        return (title, text), set(links)
    