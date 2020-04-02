import copy
import sys
import utils
from api_connector import ApiConnector
from article_reader import ArticleReader
from batch_processor import BatchProcessor
from data_saver import ArticleSaver, TitleSaver
from article_filter import ArticleFilter


args = utils.parse_args()
cfg = utils.read_config('config.json')
utils.add_path(args['dir'], cfg['files'])
afilter = ArticleFilter(**cfg['filter'])

# Get lists stored in files from previous crawls
all_discards = TitleSaver.read_title_file(cfg['files']['discarded'])
all_redirects = TitleSaver.read_title_file(cfg['files']['redirected'])
all_titles = TitleSaver.read_title_file(cfg['files']['crawled'])
prev_num_titles = len(all_titles)
tot_num_titles = prev_num_titles + cfg['max_pages']


# Get list of articles to crawl
seedfile = cfg['files']['pending'] if args['pending'] else cfg['seed']
curr_titles = TitleSaver.read_title_file(seedfile)
curr_titles -= all_discards
curr_titles -= all_redirects
all_pending = utils.limit_titles(all_titles, curr_titles, tot_num_titles)
if len(curr_titles) == 0:
    sys.exit("No new titles to crawl. Quitting...")


# Process a batch, use links from the batch in next batch, ...
all_content = []
while len(curr_titles) > 0 and len(all_content) < cfg['max_pages']:
    print("Processing batch of {} article titles...".format(len(curr_titles)))

    bproc = BatchProcessor(ApiConnector(**cfg['api']).get_parsed_text, 1, ArticleReader())
    articles = bproc.batch_call_api(curr_titles)
    contents, next_titles = bproc.read_articles(articles)

    next_titles -= all_discards
    next_titles -= all_redirects
    contents, redirects_src, redirects_dst = afilter.find_redirects(contents)
    all_redirects |= redirects_src # no need to crawl
    next_titles |= redirects_dst # add for a future batch

    next_titles, discarded_titles = afilter.filter_many(next_titles)
    all_discards |= discarded_titles

    all_pending |= utils.limit_titles(all_titles, next_titles, tot_num_titles)
    all_content.extend(contents)

    curr_titles = copy.copy(next_titles)
    next_titles = set()


# Save all data
ArticleSaver.write_content_file(cfg['files']['article_content_prefix'], all_content)
TitleSaver.write_title_file(cfg['files']['crawled'], all_titles)
TitleSaver.write_title_file(cfg['files']['pending'], all_pending)
TitleSaver.write_title_file(cfg['files']['discarded'], all_discards)
TitleSaver.write_title_file(cfg['files']['redirected'], all_redirects)
