import re


class ArticleFilter:
    ''' Identify articles that need not be crawled. 
    '''

    def __init__(self, config=None):
        self.config = config if config else {}

    def filter_one(self, title):
        return tuple()

    def filter_many(self, titles):
        for title in titles:
            self.filter_one(title)
        return tuple()
