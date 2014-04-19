# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import shutil
from dripfeed.comics import Comic, XPathComic
import os
import tempfile
from dripfeed.configs import put_config, Config
import requests
import mock


def test_put_config_creates_file():
    d = tempfile.mkdtemp()
    try:
        fname = os.path.join(d, 'test_config.cfg')
        config = Config(comic=Comic(name='blah', start_url='http://test.com/'),
                        next_url='http://test.com/',
                        rss_file='/dev/null')
        put_config(config, create_file=True, filename=fname)

        with open(fname, 'r') as f:
            content = f.read()
        assert content
        assert '[blah]' in content
    finally:
        shutil.rmtree(d)


def first_gunnerkrigg_page():
    # Stripped-down version of actual page; note the relative URL.
    result = mock.Mock()
    result.content = '''
    <html><head></head>
    <body>
      <div class="somewhere">
        <a href="?p=2"><img src='http://www.gunnerkrigg.com/images/next_a.jpg'></img></a>
      </div>
    </body>
    </html>'''
    return result


def test_run_once():
    config = Config(comic=XPathComic(name='gunnerkrigg',
                                     next_xpath="//img[@src='http://www.gunnerkrigg.com/images/next_a.jpg']/.."),
                    next_url='http://gunnerkrigg.com/?p=1')
    with mock.patch('requests.get', return_value=first_gunnerkrigg_page()):
        next_url = config.comic.next_url(config.next_url)
    assert next_url == 'http://gunnerkrigg.com/?p=2'
