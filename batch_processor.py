import copy


class BatchProcessor:
    ''' A class to process articles in batches.  
    '''

    def __init__(self):
        pass

    def batch_call_api(self, conn, titles):
        articles = []
        for i, title in enumerate(titles, start=1):
            print("{}/{}: {}...".format(i, len(titles), title))
            text = conn.request_text(title)
            articles.append((title, text))
        return articles


    def read_articles(self, reader, articles):
        all_content = []
        all_links = set()

        for title, text in articles:
            # Empty text: article doesn't exist
            if not text.strip(): continue

            content, links = reader.read(title, text)
            if content:
                all_content.append(content)
            if links:
                all_links |= links

        return all_content, all_links


