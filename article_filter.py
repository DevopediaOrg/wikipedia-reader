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
        special_pages = (
            # https://en.wikipedia.org/wiki/Help:Special_page
            'Category', 'Draft', 'File', 'Help', 'MediaWiki', 'Module',
            'Portal', 'Template', 'TimedText', 'User', 'Wikipedia',
            'Book', 'Education Program', 'Gadget', 'Gadget Definition',
            'Special', 'Media',
            # Others such as Wiktionary, MediaWiki, etc.
            'Bugzilla', 'Image', 'meta', 'mw', 's', 'wikt', 'WP',
            # https://en.wikipedia.org/wiki/List_of_Wikipedias
            'aa', 'ab', 'ace', 'ady', 'af', 'ak', 'als', 'am', 'an', 'ang', 'ar', 'arc', 'arz', 'as', 'ast', 'atj', 'av', 'ay', 'az', 'azb', 'ba', 'ban', 'bar', 'bat-smg', 'bcl', 'be', 'be-x-old', 'bg', 'bh', 'bi', 'bjn', 'bm', 'bn', 'bo', 'bpy', 'br', 'bs', 'bug', 'bxr', 'ca', 'cbk-zam', 'cdo', 'ce', 'ceb', 'ch', 'cho', 'chr', 'chy', 'ckb', 'co', 'cr', 'crh', 'cs', 'csb', 'cu', 'cv', 'cy', 'da', 'de', 'din', 'diq', 'dsb', 'dty', 'dv', 'dz', 'ee', 'el', 'eml', 'eo', 'es', 'et', 'eu', 'ext', 'fa', 'ff', 'fi', 'fiu-vro', 'fj', 'fo', 'fr', 'frp', 'frr', 'fur', 'fy', 'ga', 'gag', 'gan', 'gd', 'gl', 'glk', 'gn', 'gom', 'gor', 'got', 'gu', 'gu', 'gv', 'ha', 'hak', 'haw', 'he', 'hi', 'hif', 'ho', 'hr', 'hsb', 'ht', 'hu', 'hy', 'hz', 'ia', 'id', 'ie', 'ig', 'ii', 'ik', 'ilo', 'inh', 'io', 'is', 'it', 'iu', 'ja', 'jam', 'jbo', 'jv', 'ka', 'kaa', 'kab', 'kbd', 'kbp', 'kg', 'ki', 'kj', 'kk', 'kl', 'km', 'kn', 'ko', 'koi', 'kr', 'krc', 'ks', 'ksh', 'ku', 'kv', 'kw', 'ky', 'la', 'lad', 'lb', 'lbe', 'lez', 'lfn', 'lg', 'li', 'lij', 'lmo', 'ln', 'lo', 'lrc', 'lt', 'ltg', 'lv', 'mai', 'map-bms', 'mdf', 'mg', 'mh', 'mhr', 'mi', 'min', 'mk', 'ml', 'mn', 'mo', 'mr', 'mrj', 'ms', 'mt', 'mus', 'mwl', 'my', 'myv', 'mzn', 'na', 'nah', 'nap', 'nds', 'nds-nl', 'ne', 'new', 'ng', 'nl', 'nn', 'no', 'nov', 'nrm', 'nso', 'nv', 'ny', 'oc', 'olo', 'om', 'or', 'os', 'pa', 'pag', 'pam', 'pap', 'pcd', 'pdc', 'pfl', 'pi', 'pih', 'pl', 'pms', 'pnb', 'pnt', 'ps', 'pt', 'qu', 'rm', 'rmy', 'rn', 'ro', 'roa-rup', 'roa-tara', 'ru', 'rue', 'rw', 'sa', 'sah', 'sat', 'sc', 'scn', 'sco', 'sd', 'se', 'sg', 'sh', 'shn', 'si', 'simple', 'sk', 'sl', 'sm', 'sn', 'so', 'sq', 'sr', 'srn', 'ss', 'st', 'stq', 'su', 'sv', 'sw', 'szl', 'ta', 'tcy', 'te', 'tet', 'tg', 'th', 'ti', 'tk', 'tl', 'tn', 'to', 'tpi', 'tr', 'ts', 'tt', 'tum', 'tw', 'ty', 'tyv', 'udm', 'ug', 'uk', 'ur', 'uz', 've', 'vec', 'vep', 'vi', 'vls', 'vo', 'wa', 'war', 'wo', 'wuu', 'xal', 'xh', 'xmf', 'yi', 'yo', 'za', 'zea', 'zh', 'zh-classical', 'zh-min-nan', 'zh-yue', 'zu'
        )
        sps = '|'.join(special_pages)
        m = re.search(r'^:?({}):(.*)'.format(sps), title, re.I)
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

    def find_redirects(self, articles):
        oks = []
        redirects_src = set()
        redirects_dst = set()

        for article in articles:
            if 'redirects' in article and article['redirects']:
                for rdt in article['redirects']:
                    if 'from' in rdt:
                        # from, to, tofragment (target on dst page)
                        # redirection already done by server to dst page
                        redirects_src.add(rdt['from'])
                    elif 'title' in rdt:
                        # dst to be requested later
                        redirects_src.add(rdt['title'])
                        redirects_dst.add(article['title'])
                oks.append(article)
            else:
                m = re.search(r'^\s*#REDIRECT\s*\[\[(.*)\]\]', article['text'], flags=re.I)
                if m:
                    redirects_src.add(article['title'])
                    redirects_dst.add(m.group(1))
                else:
                    oks.append(article)
        
        return oks, redirects_src, redirects_dst