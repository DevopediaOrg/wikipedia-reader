''' A selection of utility functions.
'''


import argparse
from datetime import datetime
import json
import os
import sys


def parse_args():
    ''' Parse command line arguments. '''
    parser = argparse.ArgumentParser(description='Download articles from Wikipedia via their API.')
    parser.add_argument('-d','--dir', required=False, help='Directory within "data/" to save files. If not specified, one is created.')
    parser.add_argument('-p','--pending', action='store_true', required=False,
        help='Ignore the seed and start from pending articles.')
    parser.add_argument('-r','--restricted', action='store_true', required=False,
        help='Crawl in a restricted manner using only most relevant links.')

    args = vars(parser.parse_args())

    if args['dir'] is None and args['pending']:
        parser.print_help()
        sys.exit("\nERR: Fresh run on a new directory. Can't use -p option.")

    if args['dir'] is None:
        args['dir'] = datetime.now().strftime('%Y%h%d.%H%M%S')
    args['dir'] = "data/{}".format(args['dir'])
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