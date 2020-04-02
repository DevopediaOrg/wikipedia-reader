from datetime import datetime, timedelta
import json
import sys
import mwclient


class ApiConnector:
    ''' Call an API to request an article.
    '''

    def __init__(self, **kwargs):
        self.config = kwargs
        if 'endpoint' not in self.config or not self.config['endpoint']:
            sys.exit("ERR: API endpoint is missing in configuration. Quitting...")

        # Put defaults for some missing configurations
        if 'parse' not in self.config or not self.config['parse']:
            self.config['parse'] = 'categories|displaytitle|links|revid|sections|templates|text|wikitext'
        if 'query' not in self.config or not self.config['query']:
            self.config['query'] = {
                'categories': {
                    'clprop': 'timestamp',
                    'cllimit': 100
                },
                'extracts': { # excludes transcluded content
                    'explaintext': 1,
                    'exsectionformat' : 'wiki'
                },
                'info': {
                    'inprop': 'displaytitle|varianttitles'
                },
                'pageviews': {},
                'redirects': {
                    'rdprop': 'title',
                    'rdlimit': 500
                },
                'revisions': {}, # can't configure for multiple titles
                'templates': {
                    'tllimit': 500
                },
                'transcludedin': {
                    'tiprop': 'title|redirect',
                    'tilimit': 500
                }
            }

        self.site = mwclient.Site(self.config['endpoint'])
        self.start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')+'T00:00:00Z'

    def get_text(self, title):
        ''' Give an article title, return the full text in Wikitext format.
        The text contains unexpanded transcluded content.
        This method makes a single API call.
        '''
        content = self.site.pages[title]

        # Wikitext format: mwclient uses action=query?prop=revisions&rvprop=content|timestamp&rvlimit=1
        text = content.text()

        # These will each make a separate API call: not ideal way to use mwclient
        # content.categories(), content.embeddedin(), content.links(),
        # content.revisions(), content.templates()

        return {
            'title': title,
            'text': text
        }

    def get_parsed_text(self, title):
        ''' Given an article title, return full text in Wikitext and HTML formats.
        Other relevant information are also returned from parsing the article's text.
        HTML text contains expanded transcluded content but categories in the footer are
        excluded. Wikitext contains all unexpanded transcluded content.
        This method makes a single API call.
        '''
        try:
            content = self.site.get('parse', page=title, prop=self.config['parse'], redirects=1)
            if 'warnings' in content:
                print("WARN: Some warnings in the API response: {}".format(content['warnings']))
        except mwclient.errors.APIError:
            # one reason is that the page doesn't exist
            return {
                'title': title,
                'text': ''
            }

        # Post-processing
        content['parse']['html'] = content['parse']['text']['*']
        content['parse']['text'] = content['parse']['wikitext']['*']
        del(content['parse']['wikitext'])

        return content['parse']

    def get_info(self, titles):
        ''' Given one or more article titles, return essential information.
        All articles queried with a single API call. However, since there might be lot
        of data to retrieve, the response is often paginated, resulting in multiple calls.
        Only an extract of the article text is returned, if requested.
        '''
        childprops = {}
        for k, v in self.config['query'].items():
            childprops.update(v)

        if isinstance(titles, list): # else: called for a single title
            titles = "|".join(titles)
        props = "|".join(self.config['query'].keys())
        continues = {}

        # Call multiple times if response is paginated
        all_content = []
        num_calls = 0
        while True:
            num_calls += 1
            content = self.site.get('query', titles=titles, prop=props, redirects=1, **childprops, **continues)
            all_content.append(content)
            if 'continue' in content:
                continues = content['continue']
            else:
                break

        # Post-process the response to only what we need
        cum_content = {}
        for content in all_content:
            pages = content['query']['pages']
            for pgid, pg in pages.items():
                #if int(pgid) < 0 and 'missing' in pg:
                #    # page doesn't exist
                #    continue

                if pgid not in cum_content:
                    cum_content[pgid] = {}

                for k, v in pg.items():
                    # lists
                    if k in ('categories', 'redirects','templates', 'transcludedin'):
                        if k not in cum_content[pgid]:
                            cum_content[pgid][k] = []
                        if k == 'templates':
                            pg[k] = [t for t in v if t['ns'] == 0]
                        cum_content[pgid][k].extend(pg[k])

                    # lengths
                    elif k in ('contributors', 'pageviews'):
                        if k not in cum_content[pgid]:
                            cum_content[pgid][k] = 0
                        if k == 'contributors':
                            cum_content[pgid][k] += len(v)
                        else:
                            cum_content[pgid][k] += sum(count for dt, count in v.items() if count is not None)

                    elif k == 'extract':
                        # empty for category pages
                        # extract may not be full text, is devoid of links and other useful stuff
                        cum_content[pgid]['text'] = v

                    # others
                    else:
                        cum_content[pgid][k] = v

        # Ignore the page ID keys since these are available in the values
        cum_content = [v for k, v in cum_content.items()]

        return cum_content
