from .configs import Config

__author__ = 'tikitu'


class Comic(object):
    def __init__(self, name=None, full_name=None, start_url=None):
        self.name = name
        self.full_name = full_name or name
        self.start_url = start_url

    def next_update(self, config):
        raise NotImplementedError()

    def initial_config(self):
        return Config(comic_name=self.name, downloaded_count=0, next_url=self.start_url)


ALL = (
    Comic(name='gunnerkrigg', full_name='Gunnerkrigg Court', start_url='http://gunnerkrigg.com/?p=1'),
    Comic(name='narbonic', full_name='Narbonic',
          start_url='http://www.webcomicsnation.com/shaenongarrity/narbonic/series.php?view=archive&chapter=9763'),
)


def get_comic(name):
    if not hasattr(get_comic, '_cache'):
        get_comic._cache = dict((comic.name, comic) for comic in ALL)
    return get_comic._cache.get(name)

