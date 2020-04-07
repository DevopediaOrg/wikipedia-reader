from abc import ABC, abstractmethod
import re
import sys
from bs4 import BeautifulSoup


class Parser(ABC):
    ''' Abstract class for parsing article content.
    '''

    def __init__(self, **kwargs):
        self.config = kwargs

    @abstractmethod
    def get_links(self, text):
        pass

    def clean_link(self, link):
        # eg. 'Teletext  ' -> 'Teletext'
        clnk = link.strip()

        # eg. eBay -> EBay, iPhone -> IPhone : the latter is the URL form
        clnk = clnk[0:1].upper() + clnk[1:]

        # eg. Function (Mathematics) -> Function (mathematics): Wikipedia has a redirect
        # eg. function (Computer science) -> function (computer science): Wikipedia has no redirect
        # eg. Bash (Unix shell) -> Bash (unix shell): the latter is not a valid article
        # Ignoring due to the last example

        return clnk

    def filter_links(self, links):
        flinks = []
        for link in links:
            # ignore blanks
            if not link: continue
            
            # ignore external links
            if re.search(r'^\s*(https?:)?//', link, flags=re.I):
                continue

            # ignore edit links
            # eg. /w/index.php?title=Electric Imp&action=edit&redlink=1
            if re.search(r'^\s*/w/.*action=edit', link, flags=re.I):
                continue

            flinks.append(link)
        return flinks


class WikitextParser(Parser):
    ''' Parser for Wikitext format.
    Wikitext syntax is documented at https://en.wikipedia.org/wiki/Help:Cheatsheet
    '''

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Links are within [[]], remove targets
        self.linkpatt = r'\[\[([^#|\]]+)[#\|]?.*?\]\]'

    def add_links(self, dst, text, patt=None, flags=0):
        if patt is None: patt = self.linkpatt
        links = re.findall(patt, text, flags=flags)
        links = [self.clean_link(link) for link in links]
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

        # ---- indices ----
        # sections marked by header: eg. == A ==, == Z ==
        # may include links to categories: eg. :Category:Biotechnology, Category:Biotechnology
        # TODO Without extra sections after last alphabet index section, end links will also be retrieved
        sectexts = re.findall(r'\n==\s*[A-Z]\s*==\s*\n(.*?)(?=\n==)', text + "\n==", flags=re.S)
        for stext in sectexts:
            self.add_links(all_links, stext)

        return set(self.filter_links(all_links))

    def get_links(self, title, text):
        all_links = []

        if 'Template:' in title:
            self.add_links(all_links, text)

        #elif 'Category:' in title: TODO
        #    self.add_links(all_links, text)

        elif self.config['restricted']:
            # ---- See also ----
            # TODO Ignores See also if it's the last section (rare case?)
            # Multiple See also sections possible (but unlikely?) if another article 
            # is substituted within this one
            satexts = re.findall(r'\n==\s*See\s+also\s*==(.*?)(?=\n==)', text, flags=re.I|re.S)
            for satext in satexts:
                self.add_links(all_links, satext)

        else:
            self.add_links(all_links, text)

        # ---- Hatnote templates ----
        # https://en.wikipedia.org/wiki/Wikipedia:Hatnote#Hatnote_templates
        # Only most commonly used ones are considered:
        # https://tools.wmflabs.org/templatecount/index.php
        # {{Main|p1|p2|l1=label1|l2=label2|...|selfref=yes}}
        # {{See also|p1|p2|l1=label1|l2=label2|...|selfref=yes|category=no}}
        hats = re.findall(r'\{\{\s*(?:Main|See\s+also)\s*\|?(.*?)\}\}', text, flags=re.I|re.S)
        for hat in hats:
            links = [self.clean_link(f) for f in hat.split('|') if '=' not in f]
            all_links.extend(links)

        return set(self.filter_links(all_links))

    def get_transcludes(self, text):
        all_transcludes = []

        # ---- Article transclusion ----
        # Ignore targets
        # eg. {{:Software engineering}}
        matches = re.findall(r'\{\{:([^|#}]+).*?\}\}', text, flags=re.S)
        all_transcludes.extend(matches)

        # ---- Template transclusion ----
        # Obtain from HTML since it's hard to reduce false positives,
        # even if we limit to only those without arguments
        # {{...}} is same as {{Template:...}}
        # eg. {{Template:Software engineering}}, {{Software engineering}}
        # Ignore targets
        # matches = re.findall(r'\{\{([^|#}]+).*?\}\}', text, flags=re.M)

        return set(self.filter_links(all_transcludes))


class HtmlParser(Parser):
    ''' Parser for HTML format.
    '''

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_links(self, title, text, targets):
        print("WARN: HtmlParser.get_links() is not implemented. Skipping...")
        return set()

    def get_transcludes(self, text):
        all_transcludes = []

        # ---- Template transclusion ----
        root = BeautifulSoup(text, 'lxml')
        for css in ('.vertical-navbox', '.navbox'):
            for elem in root.select(css):
                # .navbox with .authority-control to be ignored
                if 'authority-control' in elem['class']: continue

                for a in elem.select('a'):
                    # can happen for selflinks
                    if not a.has_attr('href'): continue

                    href = re.sub(r'^/wiki/', '', a['href'])
                    href = re.sub(r'#.*', '', href.replace('_', ' '))
                    all_transcludes.append(href)

        return set(self.filter_links(all_transcludes))
