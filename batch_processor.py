import copy
import concurrent.futures


class BatchProcessor:
    ''' A class to process articles in batches.  
    '''

    def __init__(self, api_func, minibatch_size, reader, **kwargs):
        self.api_func = api_func
        self.minibatch_size = minibatch_size
        self.reader = reader
        self.config = kwargs

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

        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            futures = {executor.submit(self.api_func, mini): mini for mini in minis}
            for i, future in enumerate(concurrent.futures.as_completed(futures), start=1):
                mini = futures[future]
                try:
                    print("{}/{}: {}".format(i, len(minis), mini), flush=True)
                    content = future.result()
                    if isinstance(content, list):
                        articles.extend(content)
                    else:
                        articles.append(content)
                except Exception as exc:
                    print('%r generated an exception: %s' % (mini, exc))

        return articles


    def read_articles(self, articles):
        all_content = []
        all_links = set()
        all_transcludes = set()

        for article in articles:
            # Empty text: article doesn't exist
            if 'text' not in article or not article['text'].strip(): continue

            targets = article['targets'] if 'targets' in article else []
            if self.config['seed']:
                all_links |=  self.reader.get_seed_links(article['text'], targets)
            else:
                links, transcludes = self.reader.get_links(article['title'], article['text'], article['html'])
                all_links |=  links
                all_transcludes |= transcludes

            all_content.append(article)

        return all_content, all_links, all_transcludes


