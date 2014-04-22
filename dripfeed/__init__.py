#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""dripfeed

Usage:
  dripfeed --help
  dripfeed list
  dripfeed init <comic-name> --rss <rss-file> --url <url> --next <xpath> [--name <long-name>]
  dripfeed update <comic-name> [--debug]
  dripfeed info <comic-name>
  dripfeed remove <comic-name>

Options:
  -h --help     Show this screen.
  --version     Show version.

  --rss         Path to the RSS file for output (file will be created)
  --next        XPath expression to extract the "next" link from a comic page
  --name        Optional long name for output (the short name is usually without spaces, since it's used on commandline)
  --debug       Raise error when updating, instead of writing it into RSS

Commands:
  list    Show all configured comics
  init    Create <rss-file> and set up config for <comic-name>
  update  Update the RSS feed for <comic-name> with one entry (use cron for regular updates)
  info    Show all config information for <comic-name>
  remove  Remove all configuration for <comic-name>
"""

from __future__ import unicode_literals, print_function
import os

from .rss import parse_rss, add_error_entry, add_entry, init_rss
from docopt import docopt
from .comics import get_comic, XPathComic, remove_comic, get_configured_comics, put_comic


__version__ = "0.9.0"
__author__ = "Tikitu de Jager"
__license__ = "MIT"


def main():
    args = docopt(__doc__, version=__version__)
    run(args)


def run(args):
    if args['list']:
        list_comics()
    elif args['init']:
        create_comic(name=args['<comic-name>'], rss_file=args['<rss-file>'], next_xpath=args['<xpath>'],
                     start_url=args['<url>'], full_name=args['<long-name>'])
    elif args['update']:
        run_once(args['<comic-name>'], raise_error=args['--debug'])
    elif args['info']:
        current_info(args['<comic-name>'])
    elif args['remove']:
        if remove_comic(args['<comic-name>']):
            print('removed')
        else:
            print('not found')
    else:
        raise ValueError('Wut? {0}'.format(args))


def list_comics():
    all_configs = get_configured_comics(allow_missing_file=True)
    for config in all_configs:
        print(os.linesep.join(config.get_info()))
    if not all_configs:
        print('(no comics configured)')


def create_comic(name, rss_file, next_xpath, start_url, full_name=None):
    comic = XPathComic(name=name, next_xpath=next_xpath, full_name=full_name, start_url=start_url, rss_file=rss_file,
                       progress=None)
    put_comic(comic, create_file=True)
    init_rss(comic)


def run_once(comic_name, raise_error=False):
    comic = get_comic(comic_name)
    try:
        next_url = comic.next_url()
    except Exception as exception:
        if raise_error:
            raise
        write_error_rss(comic, exception)
    else:  # only update the config file if there was no problem
        comic.update_progress(next_url)
        put_comic(comic, overwrite=True)
        write_success_rss(comic)


def current_info(comic_name):
    config = get_comic(comic_name)
    print(os.linesep.join(config.get_info()))


def _write_rss(comic, op):
    with open(comic.rss_file, 'r+') as f:
        prev_rss = parse_rss(f)
        # feedparser closes file :-/
    op(prev_rss)
    with open(comic.rss_file, 'r+') as f:
        prev_rss.write_xml(f)
        f.truncate()


def write_error_rss(comic, exception):
    _write_rss(comic, lambda parsed_rss: add_error_entry(parsed_rss, exception))


def write_success_rss(comic):
    _write_rss(comic, lambda parsed_rss: add_entry(parsed_rss, comic))


if __name__ == '__main__':
    main()
