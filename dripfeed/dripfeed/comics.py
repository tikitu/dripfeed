from __future__ import unicode_literals, print_function
import urlparse
import requests
import lxml.html

__author__ = 'tikitu'


class Comic(object):
    def __init__(self, name=None, full_name=None, start_url=None):
        self.name = name
        self.full_name = full_name or name
        self.start_url = start_url

    def next_update(self, config):
        raise NotImplementedError()

    def add_to_global_config(self, global_config):
        global_config.set(self.name, 'long_name', self.full_name)
        global_config.set(self.name, 'start_url', self.start_url)

    def next_url(self, current_url):
        raise NotImplementedError('Subclasses must implement')


class NoMatchForXPathError(Exception):
    def __init__(self, xpath=None, url=None):
        super(NoMatchForXPathError, self).__init__('XPath expression {0} found no match in url {1}'.format(xpath, url))
        self.xpath = xpath
        self.url = url


class XPathComic(Comic):
    def __init__(self, next_xpath=None, **kwargs):
        super(XPathComic, self).__init__(**kwargs)
        self.next_xpath = next_xpath

    def next_url(self, current_url):
        page = requests.get(current_url)
        tree = lxml.html.fromstring(page.content)
        elems = tree.xpath(self.next_xpath)
        if not elems:
            raise NoMatchForXPathError(xpath=self.next_xpath, url=current_url)
        next_url = elems[0].attrib['href']
        next_url = urlparse.urljoin(current_url, next_url)  # convert relative url to absolute, e.g. ?p=2 to http://...
        return next_url

    def add_to_global_config(self, global_config):
        global_config.set(self.name, 'next_xpath', self.next_xpath)
        super(XPathComic, self).add_to_global_config(global_config)


ALL = (
    XPathComic(name='gunnerkrigg', full_name='Gunnerkrigg Court', start_url='http://gunnerkrigg.com/?p=1',
               next_xpath="//img[@src='http://www.gunnerkrigg.com/images/next_a.jpg']/.."),
    Comic(name='narbonic', full_name='Narbonic',
          start_url='http://www.webcomicsnation.com/shaenongarrity/narbonic/series.php?view=archive&chapter=9763'),
)


def get_comic(name):
    if not hasattr(get_comic, '_cache'):
        get_comic._cache = dict((comic.name, comic) for comic in ALL)
    return get_comic._cache.get(name)

