import copy
import os
import sys
import utils
from api_connector import ApiConnector
from article_reader import ArticleReader
from batch_processor import BatchProcessor
from data_saver import ArticleSaver, TitleSaver, TextSaver
from article_filter import ArticleFilter


args = utils.parse_args()
cfg = utils.read_config('config.json')
utils.add_path(args['dir'], cfg['files'])
afilter = ArticleFilter(**cfg['filter'])


# Read current level: relevant only when not seeding
try:
    curr_level = int(TextSaver.read_file(cfg['files']['curr_level']))
except FileNotFoundError:
    curr_level = 1
if curr_level > args['levels']:
    sys.exit("ERR: Already crawled all permitted levels. Quitting...")


# Get lists stored in files from previous crawls
all_discards = TitleSaver.read_title_file(cfg['files']['discarded'])
all_redirects = TitleSaver.read_title_file(cfg['files']['redirected'])
all_titles = TitleSaver.read_title_file(cfg['files']['crawled'])
all_ids = TitleSaver.read_title_file(cfg['files']['crawled_ids'])
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


# Process a batch, use links from the batch in a future batch, ...
all_content = []
while curr_level <= args['levels'] and len(curr_titles) > 0 and len(all_content) < args['maxpages']:
    if not args['seed']: print("Level {} >>>".format(curr_level))
    print("Processing batch of {} {} titles...".format(len(curr_titles), context))

    areader = ArticleReader(transcludes=cfg['transcludes'], restricted=args['restricted'])
    bproc = BatchProcessor(ApiConnector(**cfg['api']).func, 1, areader, seed=args['seed'])
    articles = bproc.batch_call_api(curr_titles)

    print("Reading {} articles...".format(len(articles)))
    contents, next_titles, trans_titles = bproc.read_articles(articles)

    # Don't add duplicates
    uniq_contents = []
    for content in contents:
        currid = str(content['pageid'])
        if currid not in all_ids:
            uniq_contents.append(content)
            all_ids.add(currid)

    if cfg['transcludes']['add_to_curr_level']:
        # Adding to current level is aggressive
        # :we also won't know how long the level will run
        # :prefer to add to next level like See also
        trans_titles -= all_discards
        trans_titles -= all_redirects
        trans_titles, discarded_titles = afilter.filter_many(trans_titles)
        all_discards |= discarded_titles
        all_pending |= trans_titles
    else:
        next_titles |= trans_titles
        trans_titles = set()

    next_titles -= all_discards
    next_titles -= all_redirects
    uniq_contents, redirects_src, redirects_dst = afilter.find_redirects(uniq_contents)
    all_redirects |= redirects_src # no need to crawl
    next_titles |= redirects_dst # add for a future batch
    all_content.extend(uniq_contents)

    # All seed articles must be crawled: discard none
    next_titles, discarded_titles = afilter.filter_many(next_titles)
    if args['seed']: discarded_titles -= all_pending
    all_discards |= discarded_titles
    all_next_pending |= next_titles

    if not all_pending:
        # Crawled all_pending fully: switch to all_next_pending
        print("Switching to next level of links...")
        if not args['seed']: curr_level += 1
        curr_titles = all_next_pending
        all_next_pending = set()
        if args['seed'] or curr_level > args['levels']:
            # only one batch when seeding
            # newly discovered links are saved but not crawled when seeding
            all_pending = curr_titles - all_titles
            curr_titles = set()
        else:
            all_pending = utils.limit_titles(all_titles, curr_titles, tot_num_titles)
        all_next_pending -= all_pending
    elif trans_titles:
        # added new transcluded content
        curr_titles = trans_titles
        all_pending = utils.limit_titles(all_titles, curr_titles, tot_num_titles)
        all_next_pending -= all_pending
    else:
        # Nothing more to crawl since reached limit in this batch
        break

# Save all data
ArticleSaver.write_content_file(cfg['files']['article_content_prefix'], all_content)
TitleSaver.write_title_file(cfg['files']['crawled'], all_titles)
TitleSaver.write_title_file(cfg['files']['crawled_ids'], all_ids)
TitleSaver.write_title_file(cfg['files']['pending'], all_pending)
TitleSaver.write_title_file(cfg['files']['next_pending'], all_next_pending)
TitleSaver.write_title_file(cfg['files']['discarded'], all_discards)
TitleSaver.write_title_file(cfg['files']['redirected'], all_redirects)
if not args['seed']:
    TextSaver.write_file(cfg['files']['curr_level'], str(curr_level))
