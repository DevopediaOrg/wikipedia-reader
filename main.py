import utils
from api_connector import ApiConnector
from article_reader import ArticleReader
from batch_processor import BatchProcessor
from data_saver import ArticleSaver, TitleSaver


args = utils.parse_args()
cfg = utils.read_config('config.json')


# Get list of articles crawled previously and stored in file
all_titles = TitleSaver.read_title_file(cfg['files']['crawled_titles'])
prev_num_titles = len(all_titles)
tot_num_titles = prev_num_titles + cfg['max_pages']


# Get list of articles to crawl
seedfile = cfg['files']['pending_titles'] if args['pending'] else cfg['files']['seed_titles']
curr_titles = TitleSaver.read_title_file(seedfile)
pending_titles = utils.limit_titles(all_titles, curr_titles, tot_num_titles)
if len(curr_titles) == 0:
    print("No new titles to crawl. Quitting...")
    exit(1)


# Process a batch, use links from the batch in next batch, ...
all_content = []
while len(curr_titles) > 0 and len(all_content) < cfg['max_pages']:
    print("\nProcessing batch of {} article titles...".format(len(curr_titles)))
    bproc = BatchProcessor()
    articles = bproc.batch_call_api(ApiConnector(), curr_titles)
    content, curr_titles = bproc.read_articles(ArticleReader(), articles)
    pending_titles |= utils.limit_titles(all_titles, curr_titles, tot_num_titles)
    all_content.extend(content)


# Save all data
ArticleSaver.write_content_file(cfg['files']['article_content_prefix'], all_content)
TitleSaver.write_title_file(cfg['files']['crawled_titles'], all_titles)
TitleSaver.write_title_file(cfg['files']['pending_titles'], pending_titles)
