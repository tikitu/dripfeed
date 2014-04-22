from __future__ import unicode_literals, print_function
import ConfigParser
import contextlib
import os
import urlparse
import portalocker
import requests
import lxml.html

__author__ = 'tikitu'


CONF_FILENAME = os.path.expanduser('~/.dripfeed.cfg')


class Comic(object):
    def __init__(self, name=None, full_name=None, start_url=None, rss_file=None, progress=None):
        self.name = name
        self.full_name = full_name or name
        self.start_url = start_url
        self.rss_file = rss_file
        self.progress = progress

    def next_update(self, config):
        raise NotImplementedError()

    def add_to_global_config(self, global_config):
        if not global_config.has_section(self.name):
            global_config.add_section(self.name)
        global_config.set(self.name, 'long_name', self.full_name)
        global_config.set(self.name, 'start_url', self.start_url)
        global_config.set(self.name, 'rss_file', self.rss_file)
        if self.progress is not None:
            self.progress.add_to_global_config(global_config, under_name=self.name)

    @property
    def current_url(self):
        return self.start_url if self.progress is None else self.progress.next_url

    def next_url(self):
        return self._next_url(self.current_url)

    def _next_url(self, current_url):
        raise NotImplementedError('Subclasses must implement')

    def update_progress(self, next_url):
        if self.progress is None:
            self.progress = Progress(episode=1, next_url=self.start_url)
        self.progress.episode += 1
        self.progress.next_url = next_url

    def get_info(self):
        result = [
            '{0}: {1}'.format(self.name, self.full_name),
            '  Outputs to {0}'.format(self.rss_file),
        ]
        if self.progress is not None:
            result.append('  Episode {0} at {1}'.format(self.progress.episode, self.progress.next_url))
        return result


class NoMatchForXPathError(Exception):
    def __init__(self, xpath=None, url=None):
        super(NoMatchForXPathError, self).__init__('XPath expression {0} found no match in url {1}'.format(xpath, url))
        self.xpath = xpath
        self.url = url


class XPathComic(Comic):
    def __init__(self, next_xpath=None, **kwargs):
        super(XPathComic, self).__init__(**kwargs)
        self.next_xpath = next_xpath

    def _next_url(self, current_url):
        page = requests.get(current_url)
        tree = lxml.html.fromstring(page.content)
        elems = tree.xpath(self.next_xpath)
        if not elems:
            raise NoMatchForXPathError(xpath=self.next_xpath, url=current_url)
        next_url = elems[0].attrib['href']
        next_url = urlparse.urljoin(current_url, next_url)  # convert relative url to absolute, e.g. ?p=2 to http://...
        return next_url

    def add_to_global_config(self, global_config):
        super(XPathComic, self).add_to_global_config(global_config)
        global_config.set(self.name, 'next_xpath', self.next_xpath)


class Progress(object):
    """
    Records how far along the comic is: episode number and current url. This information is strictly optional: if it
    is not present in the configuration file, then the comic is at its first episode and the "next url" is the start
    url for the comic.
    """

    def __init__(self, episode=1, next_url=None):
        self.episode = episode
        self.next_url = next_url

    def add_to_global_config(self, global_config, under_name):
        """
        @arg global_config: ConfigParser.ConfigParser
        """
        global_config.set(under_name, 'next_url', self.next_url)
        global_config.set(under_name, 'episode', str(self.episode))


@contextlib.contextmanager
def _locked_config_file():
    """
    Get and release lock on global config file.
    We use this whenever reading/writing (but *not* over whole program run!).
    This locking pattern makes it safe to run multiple instances concurrently, so long as they don't update the same
    comic: update Gunnerkrigg Court daily and Narbonic hourly with separate cron jobs (but don't update Narbonic hourly
    *and* daily, although why would you want to?).
    """
    filename = CONF_FILENAME
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


def get_comic(comic_name):
    with _locked_config_file() as f:
        global_config = ConfigParser.SafeConfigParser()
        global_config.readfp(f)
        return _unlocked_get_comic(comic_name, global_config)


def _unlocked_get_comic(comic_name, global_config):
    if not global_config.has_section(comic_name):
        raise ValueError(u'Comic {0} is not configured'.format(comic_name))
    if global_config.has_option(comic_name, 'next_url'):
        progress = Progress(
            episode=int(global_config.get(comic_name, 'episode', 1)),
            next_url=global_config.get(comic_name, 'next_url'),
        )
    else:
        progress = None
    comic = XPathComic(name=comic_name,
                       full_name=global_config.get(comic_name, 'long_name', None),
                       start_url=global_config.get(comic_name, 'start_url'),
                       rss_file=global_config.get(comic_name, 'rss_file'),
                       next_xpath=global_config.get(comic_name, 'next_xpath'),
                       progress=progress)
    return comic


def get_configured_comics(allow_missing_file=False):
    global_config = get_global_config(allow_missing_file=allow_missing_file)
    return [_unlocked_get_comic(comic_name, global_config) for comic_name in global_config.sections()]


def put_comic(comic, create_file=False, overwrite=False):
    """
    file creation is NOT under locking: there's no (sane) way to lock file creation safely :-/
    So be careful when you call this, with create_file=True!

    @arg comic: Comic object
    """
    filename = CONF_FILENAME
    if create_file and not os.path.isfile(filename):
        print('Creating file {0}'.format(filename))
        with open(filename, 'w') as f:
            f.write(os.linesep)
    with _locked_config_file() as f:
        global_config = ConfigParser.SafeConfigParser()
        global_config.readfp(f)
        if global_config.has_section(comic.name) and not overwrite:
            raise ValueError('Comic {0} is already configured!'.format(comic.name))
        action = 'Updating' if overwrite else 'Adding'
        print('{0} {1} in config file {2}'.format(action, comic.name, filename))
        comic.add_to_global_config(global_config)

        # Replace the *entire* file contents: this is why we need to lock so carefully!
        f.seek(0)
        global_config.write(f)
        f.truncate()


def remove_comic(comic_name):
    with _locked_config_file() as f:
        global_config = ConfigParser.ConfigParser()
        global_config.readfp(f)
        removed = global_config.remove_section(comic_name)
        f.seek(0)
        global_config.write(f)
        f.truncate()
    return removed


def get_global_config(allow_missing_file=False):
    filename = CONF_FILENAME
    if allow_missing_file and not os.path.isfile(filename):
        return ConfigParser.SafeConfigParser()
    with _locked_config_file() as f:
        global_config = ConfigParser.SafeConfigParser()
        global_config.readfp(f)
    return global_config
