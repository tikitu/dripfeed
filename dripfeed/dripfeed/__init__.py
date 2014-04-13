#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""dripfeed

Usage:
  dripfeed list
  dripfeed run <comic>
  dripfeed info <comic>

Options:
  -h --help     Show this screen.
  --version     Show version.
"""

from __future__ import unicode_literals, print_function
from docopt import docopt
from .comics import ALL as ALL_COMICS, get_comic
from .configs import get_config, put_config

__version__ = "0.1.0"
__author__ = "Tikitu de Jager"
__license__ = "MIT"


def main():
    args = docopt(__doc__, version=__version__)
    if args['list']:
        list_comics()
    elif args['run']:
        run_once(args['<comic>'])
    elif args['info']:
        current_info(args['<comic>'])
    else:
        raise ValueError('Wut? {0}'.format(args))


def list_comics():
    for comic in ALL_COMICS:
        print('{0} ({1}): {2}'.format(comic.name, comic.full_name, comic.start_url))


def run_once(comic_name):
    comic = get_comic(comic_name)
    config = get_config(comic_name)
    rss_entry, new_config = comic.next_update(config)
    put_config(new_config)
    write_rss_entry(comic_name, rss_entry)


def current_info(comic_name):
    comic = get_comic(comic_name)
    config = get_config(comic_name)
    next_url = comic.get_url(config)
    print('{0} (1): {2}'.format(comic.full_name, config.get('downloaded_count', 0), next_url))


def write_rss_entry(comic_name, entry):
    raise NotImplementedError()

if __name__ == '__main__':
    main()
