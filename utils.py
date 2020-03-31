''' A selection of utility functions.
'''


import argparse
import json
from tqdm import tqdm


def parse_args():
    ''' Parse command line arguments. '''
    parser = argparse.ArgumentParser(description='Download articles from Wikipedia via their API.')
    parser.add_argument('-p','--pending', action='store_true', required=False,
        help='Ignore the seed and start from pending articles.')
    args = vars(parser.parse_args())
    return args


def read_config(fname):
    with open(fname, 'r') as infile:
        return json.loads(infile.read())


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