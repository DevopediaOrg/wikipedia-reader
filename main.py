import argparse
import copy
import csv
import glob
import os.path
import re
from tqdm import tqdm
from api_connector import ApiConnector
from article_reader import ArticleReader


# -------------------------------------------------------------
# Initialization
# -------------------------------------------------------------
MAX_PAGES = 4
USE_CACHE = False
CONFIG = {
    'includes': ['Category']
}
FILES = {
    'seed_titles': 'data/seed_titles.txt',
    'pending_titles': 'data/pending_titles.txt',
    'crawled_titles': 'data/crawled_titles.txt',
    'article_content_prefix': 'data/ac'
}


# -------------------------------------------------------------
# Functions
# -------------------------------------------------------------
def parse_args():
    ''' Parse command line arguments. '''
    parser = argparse.ArgumentParser(description='Download articles from Wikipedia via their API.')
    parser.add_argument('-p','--pending', action='store_true', required=False,
        help='Ignore the seed and start from file {}.'.format(FILES['pending_titles']))
    args = vars(parser.parse_args())
    return args


def limit_titles(all_titles, titles, limit=MAX_PAGES):
    '''Both arguments are modified. Returns excluded titles.'''
    pending_titles = set()

    new_titles = titles - all_titles # remove overlaps
    while len(all_titles) + len(new_titles) > limit:
        pending_titles.add(new_titles.pop())
    all_titles |= new_titles
    titles.clear()
    titles |= new_titles

    return pending_titles

def batch_call_api(titles):
    conn = ApiConnector()

    articles = []
    for title in tqdm(titles):
        print("\n{}...".format(title))
        text = conn.request_text(title)
        articles.append((title, text))

    return articles


def read_articles(articles):
    reader = ArticleReader()

    all_content = []
    all_links = set()
    for title, text in articles:
        content, links = reader.read(title, text)
        if content:
            all_content.append(content)
        if links:
            all_links |= links

    return all_content, all_links


def read_content_file(fname, fields):
    content = []

    try:
        csv.field_size_limit(1000000)
        with open(fname, 'r', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                values = tuple(row[f] for f in fields)
                if len(values) > 1:
                    content.append(values)
                else: # only one field requested
                    content.append(values[0])
    except FileNotFoundError:
        pass

    return content


def write_content_file(fname, content):
    # Derive the next filename suffix
    acfiles = glob.glob(FILES['article_content_prefix']+'*')
    if acfiles:
        nextid = 1 + max(int(re.sub(r'.*-(\d+)\.csv$', r'\1', os.path.basename(f))) for f in acfiles)
    else:
        nextid = 0
    fname = "{}-{}.csv".format(fname, nextid)

    with open(fname, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=['Title', 'Text'])
        writer.writeheader()
        for c in content:
            writer.writerow({'Title': c[0].encode(), 'Text': c[1].encode()})


def read_title_file(fname):
    try:
        with open(fname, "r", encoding='utf-8') as infile:
            titles = set([line.strip() for line in infile.readlines()])
    except FileNotFoundError:
        titles = set()
    return titles


def write_title_file(fname, titles):
    with open(fname, "w", encoding='utf-8') as outfile:
        for t in titles:
            outfile.write(t + "\n")


# -------------------------------------------------------------
# Main processing
# -------------------------------------------------------------
args = parse_args()

# Get list of articles crawled previously and stored in file
all_titles = read_title_file(FILES['crawled_titles'])
prev_num_titles = len(all_titles)
tot_num_titles = prev_num_titles + MAX_PAGES

# Get list of articles to crawl
seedfile = FILES['pending_titles'] if args['pending'] else FILES['seed_titles']
curr_titles = read_title_file(seedfile)
print(seedfile, len(all_titles), len(curr_titles), '-')
pending_titles = limit_titles(all_titles, curr_titles, tot_num_titles)
print(seedfile, len(all_titles), len(curr_titles), len(pending_titles))

if len(curr_titles) == 0:
    print("No new titles to crawl. Quitting...")
    exit(1)

# Process a batch, use links from the batch in next batch, ...
all_content = []
while len(curr_titles) > 0 and len(all_content) < MAX_PAGES:
    print("\nProcessing batch of {} article titles...".format(len(curr_titles)))
    reader = ArticleReader()
    articles = batch_call_api(curr_titles)
    content, curr_titles = read_articles(articles)
    pending_titles |= limit_titles(all_titles, curr_titles, tot_num_titles)
    all_content.extend(content)

# Save all data
if all_content:
    write_content_file(FILES['article_content_prefix'], all_content)
write_title_file(FILES['crawled_titles'], all_titles)
write_title_file(FILES['pending_titles'], pending_titles)
