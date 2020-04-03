''' A selection of utility functions.
'''


import argparse
from datetime import datetime
import json
import os
import sys


def parse_args():
    ''' Parse command line arguments. '''
    now = datetime.now().strftime('%Y%h%d.%H%M%S')
    maxpages = 100

    parser = argparse.ArgumentParser(description='Download articles from Wikipedia via their API.')
    parser.add_argument('-b','--basepath', required=False, default='output',
        help='Base path to folder where files will be saved. If not specified, \'output/\' folder is used.')
    parser.add_argument('-d','--dir', required=False, default=now,
        help='Directory within the base path to save files. If not specified, create one based on current datetime.')
    parser.add_argument('-m','--maxpages', required=False, default=maxpages, type=int,
        help='Maximum number of pages to crawl. Default is {}. Range is 1-1000.'.format(maxpages))
    parser.add_argument('-r','--restricted', action='store_true', required=False,
        help='Parse article content in a restricted manner to identify more articles to crawl.')
    parser.add_argument('-s','--seed', action='store_true', required=False,
        help='Crawl seed articles to discover other articles to crawl. The latter are added to pending list.')

    args = vars(parser.parse_args())
 
    # Input validation
    if not args['seed'] and args['dir'] != now and \
       not os.path.exists(os.path.join(args['basepath'], args['dir'])):
        parser.print_help()
        sys.exit("\nERR: Can't crawl articles. First seed using -s option.")
    if args['maxpages'] < 1 or args['maxpages'] > 1000:
        parser.print_help()
        sys.exit("\nERR: Out of range. Range for -m option is 1-1000.")

    args['dir'] = "{}/{}".format(args['basepath'], args['dir'])
    try: os.makedirs(args['dir'])
    except FileExistsError: pass

    return args


def read_config(fname):
    with open(fname, 'r') as infile:
        return json.loads(infile.read())


def add_path(path, files):
    for k, v in files.items():
        files[k] = "{}/{}".format(path, v)


def limit_titles(all_titles, titles, limit):
    '''Both arguments are modified. Returns excluded titles.'''
    pending_titles = set()

    new_titles = titles - all_titles # remove overlaps
    while len(all_titles) + len(new_titles) > limit:
        pending_titles.add(new_titles.pop())
    all_titles |= new_titles
    titles.clear()
    titles |= new_titles

    return pending_titles