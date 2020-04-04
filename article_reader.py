from abc import ABC, abstractmethod
import re
import sys


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

        # Links are within [[]], remove targets
        self.linkpatt = r'\[\[([^#|\]]+)[#\|]?.*?\]\]'

    def add_links(self, dst, text, patt=None, flags=0):
        if patt is None: patt = self.linkpatt
        links = re.findall(patt, text, flags=flags)
        dst.extend(links)

    def get_seed_links(self, text, targets):
        targets = '|'.join(targets) if targets else '.*?'

        all_links = []

        # When using a seed, get links based on page type
        # Page types: https://en.wikipedia.org/wiki/Wikipedia:Contents/Technology_and_applied_sciences

        # ---- overviews ----
        # optional: targets (separated by |) are used to specify sections to consider
        # sections marked by header: eg. : '''''[[Computing]]''''', :: '''''[[Computing]]'''''
        # TODO Without extra sections after last section, end links will also be retrieved
        sectexts = re.findall(
            r"\n(?P<start>:+)\s*'''''\s*\[\[(?:{})\]\]'''''(.*?)(?=\n(?P=start)[^:])".format(targets),
            text + "\n:::::::", flags=re.S)
        ftext = ' '.join(stext[1] for stext in sectexts)
        self.add_links(all_links, ftext)

        # ---- outlines ----
        # ---- lists ----
        # optional: targets (separated by |) are used to specify sections to consider
        if targets:
            sectexts = re.findall(
                r"\n(?P<start>=+)\s*(?:{})\s*(?P=start)\s*\n(.*?)(?=\n(?P=start)[^=])".format(targets),
                text+"\n========", flags=re.S)
            ftext = ' '.join(stext[1] for stext in sectexts)
        else:
            ftext = text
        # list items: lines that start with: * [[...]], ** [[...]]
        # list items in table: lines that start with: | [[...]]
        # Side-effect: captures See also list items
        patt = r'^\s*(?:\*+|\|)\s*{}'.format(self.linkpatt)
        self.add_links(all_links, ftext, patt, re.I|re.M)

        # ---- portals ----
        # Ignored because it's not useful

        # ---- glossaries ----
        # eg. {{term|1=analog recording|2=[[analog recording]]}}, {{term|[[action language]]}}
        patt = r'\{\{term\|.*?' + self.linkpatt + r'.*?\}\}'
        self.add_links(all_links, text, patt, re.M)

        # ---- categories ----
        # Too many to enumerate in seed file
        # Ignored because it can bring in unrelated content

        # ---- indices ----
        # sections marked by header: eg. == A ==, == Z ==
        # may include links to categories: eg. :Category:Biotechnology, Category:Biotechnology
        # TODO Without extra sections after last alphabet index section, end links will also be retrieved
        sectexts = re.findall(r'\n==\s*[A-Z]\s*==\s*\n(.*?)(?=\n==)', text + "\n==", flags=re.S)
        for stext in sectexts:
            self.add_links(all_links, stext)

        all_links = {lnk.strip() for lnk in all_links}

        return all_links

    def get_links(self, text):
        all_links = []

        if self.config['restricted']:
            # ---- See also ----
            # TODO Ignores See also if it's the last section (rare case for relevant articles)
            m = re.search(r'.*\n==\s*See also\s*==\s*\n(.*?)\n==.*', text, flags=re.I|re.S)
            if m:
                self.add_links(all_links, m.group(1))

            # ---- Transclusions ----
            # Template: eg. {{Software engineering}}, {{Software engineering|state=off}}
            # Article: eg. {{:Software engineering}}
            #m = re.search(r'.*\{\{\s*([^|]+?).*?\}\}.*', text, flags=re.S)
            #if m:
            #    self.add_links(all_links, m.group(1))

        else:
            self.add_links(all_links, text)

        all_links = {lnk.strip() for lnk in all_links}

        return all_links


class HtmlReader(ArticleReader):
    ''' Article reader for HTML format.
    '''

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        sys.exit("ERR: HtmlReader is not implemented. Quitting...")

    def get_links(self, text, targets):
        pass

