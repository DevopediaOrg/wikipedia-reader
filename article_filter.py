import re
import string
import spacy


class ArticleFilter:
    ''' Identify articles that need not be crawled. 
    '''

    def __init__(self, **kwargs):
        self.config = kwargs
        self.sp_en = spacy.load('en_core_web_sm')
        self.read_common_words()

    def read_common_words(self):
        if 'common_word_file' not in self.config:
            self.common_words = set()
        else:
            with open(self.config['common_word_file'], 'r', encoding='utf-8') as f:
                self.common_words = set([word.strip() for word in f.readlines()])

    def is_allowed(self, title):
        # Special pages (controlled by config)
        # https://en.wikipedia.org/wiki/Help:Special_page
        m = re.search(r'^:?(\w+):(.*)', title)
        mod_title = title
        if m:
            if 'includes' not in self.config or m.group(1) not in self.config['includes']:
                return False
            else:
                mod_title = m.group(2)

        # Ignore proper nouns
        # :ignore stopwords, more than one word and all starting with uppercase
        # :remove (): eg. Kenneth D. Bailey (sociologist) --> Kenneth D. Bailey
        mod_title = re.sub(r'\s*\(.*\)\s*', '', mod_title)
        words = [w for w in re.split(r'\W+', mod_title) if w and w not in self.sp_en.Defaults.stop_words]
        if len(words) > 1 and all(w[0] in string.ascii_uppercase for w in words):
            return False

        return True

    def filter_many(self, titles):
        oks = set()
        kos = set()
        for title in titles:
            if self.is_allowed(title):
                oks.add(title)
            else:
                kos.add(title)
        return oks, kos

    def find_redirects(self, content):
        oks = []
        redirects_src = set()
        redirects_dst = set()

        for (title, text) in content:
            m = re.search(r'^#REDIRECT\s+\[\[(.*)\]\]', text)
            if m:
                redirects_src.add(title)
                redirects_dst.add(m.group(1))
            else:
                oks.append((title, text))
        
        return oks, redirects_src, redirects_dst