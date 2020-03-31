import mwclient


class ApiConnector:
    ''' Call an API to request an article. 
    '''

    def __init__(self, endpoint='en.wikipedia.org'):
        self.endpoint = endpoint
        self.site = mwclient.Site('en.wikipedia.org')

    def request_text(self, title):
        content = self.site.pages[title]
        return content.text()
