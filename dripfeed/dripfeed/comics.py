from .configs import Config
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

    def initial_config(self, rss_filename):
        return Config(comic_name=self.name, downloaded_count=0, next_url=self.start_url, rss_file=rss_filename)


class XPathComic(Comic):
    def __init__(self, next_xpath=None, **kwargs):
        super(XPathComic, self).__init__(**kwargs)
        self.next_xpath = next_xpath

    def next_update(self, config):
        page = requests.get(config.next_url)
        tree = lxml.html.fromstring(page.content)
        elems = tree.xpath(self.next_xpath)
        config = Config(comic_name=config.comic_name,
                        downloaded_count=config.downloaded_count + 1,
                        next_url=elems[0].attrib['href'],
                        rss_file=config.rss_file)
        return config.next_url, config


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

