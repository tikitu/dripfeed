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
from .comics import ALL as ALL_COMICS

__version__ = "0.1.0"
__author__ = "Tikitu de Jager"
__license__ = "MIT"


def main():
    '''Main entry point for the dripfeed CLI.'''
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
        print('{0} ({1}) {2}'.format(comic.name, comic.full_name, comic.start_url))


def run_once(comic):
    raise NotImplementedError()


def current_info(comic):
    raise NotImplementedError()


if __name__ == '__main__':
    main()
