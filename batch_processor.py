import copy


class BatchProcessor:
    ''' A class to process articles in batches.  
    '''

    def __init__(self, api_func, minibatch_size, reader):
        self.api_func = api_func
        self.minibatch_size = minibatch_size
        self.reader = reader

    def batch_call_api(self, titles):
        articles = []

        # Mini-batch of minibatch_size titles in a single API call
        minis = []
        if self.minibatch_size > 1:
            titles = tuple(titles)
            for i in range(0, len(titles), self.minibatch_size):
                minis.append(titles[i:i+self.minibatch_size])
        else:
            minis = titles

        for i, mini in enumerate(minis, start=1):
            print("{}/{}: {}...".format(i, len(minis), mini))
            content = self.api_func(mini)
            if isinstance(content, list):
                articles.extend(content)
            else:
                articles.append(content)

        return articles


    def read_articles(self, articles):
        all_content = []
        all_links = set()

        for article in articles:
            # Empty text: article doesn't exist
            if 'text' not in article or not article['text'].strip(): continue

            targets = article['targets'] if 'targets' in article else []
            if self.reader.config['seed']:
                all_links |=  self.reader.get_seed_links(article['text'], targets)
            else:
                all_links |=  self.reader.get_links(article['text'])

            all_content.append(article)

        return all_content, all_links


