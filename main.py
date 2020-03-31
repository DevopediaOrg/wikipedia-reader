import copy
import utils
from api_connector import ApiConnector
from article_reader import ArticleReader
from batch_processor import BatchProcessor
from data_saver import ArticleSaver, TitleSaver
from article_filter import ArticleFilter


args = utils.parse_args()
cfg = utils.read_config('config.json')
afilter = ArticleFilter(**cfg['filter'])


# Get lists stored in files from previous crawls
all_discards = TitleSaver.read_title_file(cfg['files']['discarded_titles'])
all_redirects = TitleSaver.read_title_file(cfg['files']['redirected_titles'])
all_titles = TitleSaver.read_title_file(cfg['files']['crawled_titles'])
prev_num_titles = len(all_titles)
tot_num_titles = prev_num_titles + cfg['max_pages']


# Get list of articles to crawl
seedfile = cfg['files']['pending_titles'] if args['pending'] else cfg['files']['seed_titles']
curr_titles = TitleSaver.read_title_file(seedfile)
curr_titles -= all_discards
curr_titles -= all_redirects
all_pending = utils.limit_titles(all_titles, curr_titles, tot_num_titles)
if len(curr_titles) == 0:
    print("No new titles to crawl. Quitting...")
    exit(1)


# Process a batch, use links from the batch in next batch, ...
all_content = []
while len(curr_titles) > 0 and len(all_content) < cfg['max_pages']:
    print("\nProcessing batch of {} article titles...".format(len(curr_titles)))

    bproc = BatchProcessor()
    articles = bproc.batch_call_api(ApiConnector(), curr_titles)
    content, next_titles = bproc.read_articles(ArticleReader(), articles)

    next_titles -= all_discards
    next_titles -= all_redirects
    content, redirects_src, redirects_dst = afilter.find_redirects(content)
    all_redirects |= redirects_src # no need to crawl
    next_titles |= redirects_dst # add for a future batch

    next_titles, discarded_titles = afilter.filter_many(next_titles)
    all_discards |= discarded_titles

    all_pending |= utils.limit_titles(all_titles, next_titles, tot_num_titles)
    all_content.extend(content)

    curr_titles = copy.copy(next_titles)
    next_titles = set()

# Save all data
ArticleSaver.write_content_file(cfg['files']['article_content_prefix'], all_content)
TitleSaver.write_title_file(cfg['files']['crawled_titles'], all_titles)
TitleSaver.write_title_file(cfg['files']['pending_titles'], all_pending)
TitleSaver.write_title_file(cfg['files']['discarded_titles'], all_discards)
TitleSaver.write_title_file(cfg['files']['redirected_titles'], all_redirects)
