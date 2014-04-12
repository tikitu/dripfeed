__author__ = 'tikitu'


class Comic(object):
    def __init__(self, name=None, full_name=None, start_url=None):
        self.name = name
        self.full_name = full_name or name
        self.start_url = start_url

    def get_next_url(self, current_url):
        raise NotImplementedError()


ALL = (
    Comic(name='gunnerkrigg', full_name='Gunnerkrigg Court', start_url='http://gunnerkrigg.com/?p=1'),
    Comic(name='narbonic', full_name='Narbonic',
          start_url='http://www.webcomicsnation.com/shaenongarrity/narbonic/series.php?view=archive&chapter=9763'),
)