from abc import ABC, abstractmethod
import re


class ArticleReader(ABC):
    ''' Abstract class for reading article text.
    Parsers for the reader must be implemented in subclasses.
    '''

    def __init__(self, **kwargs):
        self.config = kwargs

    @abstractmethod
    def get_links(self, text):
        pass


class WikitextReader(ArticleReader):
    ''' Article reader for Wikitext format.
    Wikitext syntax is documented at
    https://en.wikipedia.org/wiki/Help:Cheatsheet
    '''

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_links(self, text):
        # Use only See also section
        if self.config['restricted']:
            text = re.sub(r'.*\n\s*==\s*See also\s*==\s*\n(.*?)\n\s*==.*', r'\1', text, flags=re.I|re.DOTALL)

        # Links are within [[]], remove targets
        return set(re.findall(r'\[\[([^#|\]]+)[#\|]?.*?\]\]', text))


class HtmlReader(ArticleReader):
    ''' Article reader for HTML format.
    '''

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_links(self, text):
        pass

