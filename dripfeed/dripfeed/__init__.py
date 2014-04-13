#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""dripfeed

Usage:
  dripfeed list [--all]
  dripfeed init <comic> <rss_file>
  dripfeed run <comic>
  dripfeed info <comic>

Options:
  -h --help     Show this screen.
  --version     Show version.

Commands:
  list                     Show active comics, or all available comics with --all
  init <comic> <rss_file>  Create <rss_file> and set up config for <comic>
  run <comic>              Update the RSS feed for <comic> with one entry (use cron for regular updates)
  info <comic>             Show all config information for <comic>
"""

from __future__ import unicode_literals, print_function
from docopt import docopt
from .comics import ALL as ALL_COMICS, get_comic
from .configs import get_config, put_config, Config, get_global_config
import simplejson as json

__version__ = "0.1.0"
__author__ = "Tikitu de Jager"
__license__ = "MIT"


def main():
    args = docopt(__doc__, version=__version__)
    run(args)


def run(args):
    if args['list']:
        list_comics(args['--all'])
    elif args['init']:
        create_config(args['<comic>'], args['<rss_file>'])
    elif args['run']:
        run_once(args['<comic>'])
    elif args['info']:
        current_info(args['<comic>'])
    else:
        raise ValueError('Wut? {0}'.format(args))


def list_comics(show_unstarted):
    global_config = get_global_config(allow_missing_file=True)
    got_any = False
    for comic in ALL_COMICS:
        if comic.name in global_config or show_unstarted:
            print('{0} ({1}): {2}'.format(comic.name, comic.full_name, comic.start_url))
        if comic.name in global_config:
            config = Config(comic_name=comic.name, **global_config[comic.name])
            print('  At episode {0}: {1}'.format(config.downloaded_count, config.next_url))
            got_any = True
    if not got_any:
        print('(no comics configured for download)')


def create_config(comic_name, rss_filename):
    comic = get_comic(comic_name)
    config = comic.initial_config(rss_filename)
    put_config(config, create_file=True)


def run_once(comic_name):
    comic = get_comic(comic_name)
    config = get_config(comic_name)
    rss_entry, new_config = comic.next_update(config)
    put_config(new_config, overwrite=True)
    write_rss_entry(comic_name, rss_entry)


def current_info(comic_name):
    comic = get_comic(comic_name)
    config = get_config(comic_name)
    if config.is_configured():
        print('{0} (ep. {1}): {2}'.format(comic.full_name, config.downloaded_count, config.rss_file))
    else:
        print('{0} (no rss)'.format(comic.full_name))


def write_rss_entry(comic_name, entry):
    raise NotImplementedError()

if __name__ == '__main__':
    main()
