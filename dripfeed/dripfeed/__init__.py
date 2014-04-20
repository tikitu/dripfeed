#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""dripfeed

Usage:
  dripfeed --help
  dripfeed list
  dripfeed init <comic-name> --rss <rss-file> --url <url> --next <xpath> [--name <long-name>]
  dripfeed run <comic-name>
  dripfeed info <comic-name>
  dripfeed remove <comic-name>

Options:
  -h --help     Show this screen.
  --version     Show version.

  --rss         Path to the RSS file for output (file will be created)
  --next        XPath expression to extract the "next" link from a comic page
  --name        Optional long name for output (the short name is usually without spaces, since it's used on commandline)

Commands:
  list  Show all configured comics
  init  Create <rss-file> and set up config for <comic-name>
  run   Update the RSS feed for <comic> with one entry (use cron for regular updates)
  info  Show all config information for <comic>
"""

from __future__ import unicode_literals, print_function
import os
from docopt import docopt
from .comics import get_comic, XPathComic
from .configs import get_config, put_config, Config, get_global_config, get_configured_comics, remove_config

__version__ = "0.1.0"
__author__ = "Tikitu de Jager"
__license__ = "MIT"


def main():
    args = docopt(__doc__, version=__version__)
    run(args)


def run(args):
    if args['list']:
        list_comics()
    elif args['init']:
        create_config(name=args['<comic-name>'], rss=args['<rss-file>'], next_xpath=args['<xpath>'],
                      start_url=args['<url>'], full_name=args['<long-name>'])
    elif args['run']:
        run_once(args['<comic-name>'])
    elif args['info']:
        current_info(args['<comic-name>'])
    elif args['remove']:
        if remove_config(args['<comic-name>']):
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


def create_config(name, rss, next_xpath, start_url, full_name=None):
    comic = XPathComic(name=name, next_xpath=next_xpath, full_name=full_name, start_url=start_url)
    config = Config(comic=comic,
                    next_url=start_url,
                    rss_file=rss)
    put_config(config, create_file=True)


def run_once(comic_name):
    config = get_config(comic_name)
    try:
        next_url = config.comic.next_url(config.next_url)
    except Exception as exception:
        write_error_rss(config, exception)
    else:  # only update the config file if there was no problem
        config.next_url = next_url
        config.episode += 1
        put_config(config, overwrite=True)
        write_success_rss(config)


def current_info(comic_name):
    config = get_config(comic_name)
    print(os.linesep.join(config.get_info()))


def write_error_rss(config, exception):
    raise NotImplementedError()


def write_success_rss(config):
    raise NotImplementedError()

if __name__ == '__main__':
    main()
