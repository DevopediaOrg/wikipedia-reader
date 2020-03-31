import copy
from tqdm import tqdm


class BatchProcessor:
    ''' A class to process articles in batches.  
    '''

    def __init__(self):
        pass

    def batch_call_api(self, conn, titles):
        articles = []
        for title in tqdm(titles):
            print("\n{}...".format(title))
            text = conn.request_text(title)
            articles.append((title, text))

        return articles


    def read_articles(self, reader, articles):
        all_content = []
        all_links = set()
        for title, text in articles:
            content, links = reader.read(title, text)
            if content:
                all_content.append(content)
            if links:
                all_links |= links

        return all_content, all_links


