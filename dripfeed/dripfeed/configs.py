from __future__ import unicode_literals, print_function
import ConfigParser
import contextlib
from dripfeed.comics import XPathComic
import os
import portalocker

__author__ = 'tikitu'


class Config(object):

    FILENAME = os.path.expanduser('~/.dripfeed.cfg')

    def __init__(self, comic=None, episode=1, next_url=None, rss_file=None):
        self.comic = comic
        self.episode = episode
        self.next_url = next_url
        self.rss_file = os.path.abspath(rss_file) if rss_file else None

    def is_configured(self):
        return bool(self.rss_file)

    def add_to_global_config(self, global_config):
        """
        @arg global_config: ConfigParser.ConfigParser
        """
        global_config.add_section(self.comic.name)
        self.comic.add_to_global_config(global_config)
        global_config.set(self.comic.name, 'rss_file', self.rss_file)
        global_config.set(self.comic.name, 'next_url', self.next_url)
        global_config.set(self.comic.name, 'episode', str(self.episode))

    def get_info(self):
        return [
            '{0}: {1}'.format(self.comic.name, self.comic.full_name),
            '  Episode {0} at {1}'.format(self.episode, self.next_url),
            '  Outputs to {0}'.format(self.rss_file)
        ]


@contextlib.contextmanager
def _locked_config_file(filename=Config.FILENAME):
    """
    Get and release lock on global config file.
    We use this whenever reading/writing (but *not* over whole program run!).
    This locking pattern makes it safe to run multiple instances concurrently, so long as they don't update the same
    comic: update Gunnerkrigg Court daily and Narbonic hourly with separate cron jobs (but don't update Narbonic hourly
    *and* daily, although why would you want to?).
    """
    if not all((os.path.isfile(filename),
                os.access(filename, os.R_OK),
                os.access(filename, os.W_OK))):
        raise ValueError('File {0} either does not exist or is not read/writeable.'.format(filename))
    fh = None
    try:
        fh = open(filename, 'r+')
        portalocker.lock(fh, portalocker.LOCK_EX)
        yield fh
    finally:
        if fh is not None:
            fh.close()


def get_config(comic_name):
    with _locked_config_file() as f:
        global_config = ConfigParser.SafeConfigParser()
        global_config.readfp(f)
        return _unlocked_get_config(comic_name, global_config)


def _unlocked_get_config(comic_name, global_config):
    if not global_config.has_section(comic_name):
        raise ValueError(u'Comic {0} is not configured'.format(comic_name))
    comic = XPathComic(name=comic_name,
                       full_name=global_config.get(comic_name, 'long_name', None),
                       start_url=global_config.get(comic_name, 'start_url'),
                       next_xpath=global_config.get(comic_name, 'next_xpath'))
    config = Config(comic=comic,
                    episode=int(global_config.get(comic_name, 'episode', 1)),
                    next_url=global_config.get(comic_name, 'next_url', comic.start_url),
                    rss_file=global_config.get(comic_name, 'rss_file'))
    return config


def get_configured_comics(allow_missing_file=False):
    global_config = get_global_config(allow_missing_file=allow_missing_file)
    return [_unlocked_get_config(comic_name, global_config) for comic_name in global_config.sections()]


def put_config(config, create_file=False, filename=Config.FILENAME, overwrite=False):
    """
    file creation is NOT under locking: there's no (sane) way to lock file creation safely :-/
    So be careful when you call this, with create_file=True!

    @arg config: Config object
    """
    if create_file and not os.path.isfile(filename):
        print('Creating file {0}'.format(filename))
        with open(filename, 'w') as f:
            f.write(os.linesep)
    with _locked_config_file(filename=filename) as f:
        global_config = ConfigParser.SafeConfigParser()
        global_config.readfp(f)
        if global_config.has_section(config.comic.name) and not overwrite:
            raise ValueError('Comic {0} is already configured!'.format(config.comic.name))
        print('Adding {0} to config file {1}'.format(config.comic.name, filename))
        config.add_to_global_config(global_config)

        # Replace the *entire* file contents: this is why we need to lock so carefully!
        f.seek(0)
        global_config.write(f)
        f.truncate()


def remove_config(comic_name, filename=Config.FILENAME):
    with _locked_config_file(filename=filename) as f:
        global_config = ConfigParser.ConfigParser()
        global_config.readfp(f)
        removed = global_config.remove_section(comic_name)
        f.seek(0)
        global_config.write(f)
        f.truncate()
    return removed


def get_global_config(allow_missing_file=False, filename=Config.FILENAME):
    if allow_missing_file and not os.path.isfile(filename):
        return ConfigParser.SafeConfigParser()
    with _locked_config_file(filename=filename) as f:
        global_config = ConfigParser.SafeConfigParser()
        global_config.readfp(f)
    return global_config
