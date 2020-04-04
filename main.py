import copy
import os
import sys
import utils
from api_connector import ApiConnector
from article_reader import HtmlReader, WikitextReader
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
all_next_pending = TitleSaver.read_title_file(cfg['files']['next_pending'])
prev_num_titles = len(all_titles)
tot_num_titles = prev_num_titles + args['maxpages']


# Are we seeding or crawling articles?
if args['seed']:
    startfile = cfg['seed']
    context = 'seed'
    fields = os.path.split(cfg['files']['article_content_prefix'])
    cfg['files']['article_content_prefix'] = os.path.join(*fields[:-1], 'seed.{}'.format(fields[-1]))
else:
    startfile = cfg['files']['pending']
    context = 'article'


# Get list of articles to crawl
curr_titles = TitleSaver.read_title_file(startfile)
curr_titles -= all_discards
curr_titles -= all_redirects
all_pending = utils.limit_titles(all_titles, curr_titles, tot_num_titles)
if len(curr_titles) == 0:
    sys.exit("No new titles to crawl. Quitting...")


# Process a batch, use links from the batch in next batch, ...
all_content = []
while len(curr_titles) > 0 and len(all_content) < args['maxpages']:
    print("Processing batch of {} {} titles...".format(len(curr_titles), context))

    if cfg['reader']['format'] == 'html':
        areader = HtmlReader(**cfg['reader'], seed=args['seed'], restricted=args['restricted'])
    else:
        areader = WikitextReader(**cfg['reader'], seed=args['seed'], restricted=args['restricted'])

    bproc = BatchProcessor(ApiConnector(**cfg['api']).func, 1, areader)
    articles = bproc.batch_call_api(curr_titles)
    contents, next_titles = bproc.read_articles(articles)

    next_titles -= all_discards
    next_titles -= all_redirects
    contents, redirects_src, redirects_dst = afilter.find_redirects(contents)
    all_redirects |= redirects_src # no need to crawl
    next_titles |= redirects_dst # add for a future batch

    # All seed articles must be crawled: discard none
    next_titles, discarded_titles = afilter.filter_many(next_titles)
    if args['seed']: discarded_titles -= all_pending
    all_discards |= discarded_titles
    all_next_pending |= next_titles

    if not all_pending:
        print("Switching to next level of links...")
        curr_titles = all_next_pending
        all_next_pending = set()
        all_pending = utils.limit_titles(all_titles, curr_titles, tot_num_titles)
    all_content.extend(contents)

    if args['seed']:
        # only one batch when seeding
        # newly discovered links are saved but not crawled when seeding
        curr_titles = set()


# Save all data
ArticleSaver.write_content_file(cfg['files']['article_content_prefix'], all_content)
TitleSaver.write_title_file(cfg['files']['crawled'], all_titles)
TitleSaver.write_title_file(cfg['files']['pending'], all_pending)
TitleSaver.write_title_file(cfg['files']['next_pending'], all_next_pending - all_pending)
TitleSaver.write_title_file(cfg['files']['discarded'], all_discards)
TitleSaver.write_title_file(cfg['files']['redirected'], all_redirects)
