import copy


class BatchProcessor:
    ''' A class to process articles in batches.  
    '''

    def __init__(self):
        pass

    def batch_call_api(self, api_func, titles, minibatch_size):
        articles = []

        # Mini-batch of minibatch_size titles in a single API call
        minis = []
        if minibatch_size > 1:
            titles = tuple(titles)
            for i in range(0, len(titles), minibatch_size):
                minis.append(titles[i:i+minibatch_size])
        else:
            minis = titles

        for i, mini in enumerate(minis, start=1):
            print("{}/{}: {}...".format(i, len(minis), mini))
            content = api_func(mini)
            if isinstance(content, list):
                articles.extend(content)
            else:
                articles.append(content)

        return articles


    def read_articles(self, reader, articles):
        all_content = []
        all_links = set()

        for article in articles:
            # Empty text: article doesn't exist
            if 'text' not in article or not article['text'].strip(): continue

            all_links |=  reader.get_links(article['text'])

            all_content.append(article)

        return all_content, all_links


