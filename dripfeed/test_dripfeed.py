# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import shutil
from datetime import datetime, timedelta
from StringIO import StringIO
from dripfeed.comics import Comic, XPathComic
from dripfeed.rss import parse_rss
import os
import tempfile
from dripfeed.configs import put_config, Config
import mock
import PyRSS2Gen as rss_gen
import feedparser as rss_parse


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


def test_absolute_url():
    # Making sure that the treatment of *relative* URLs still lets *absolute* URLs work if we get those
    config = Config(comic=XPathComic(name='blah', next_xpath='//a'), next_url='http://base.com/')
    with mock.patch('requests.get', return_value=mock.Mock()) as get_mock:
        get_mock.return_value.content = '<a href="http://elsewhere.com/">'
        next_url = config.comic.next_url(config.next_url)
    assert next_url == 'http://elsewhere.com/'


def test_round_tip_rss():
    now = datetime.utcnow().replace(microsecond=0)
    feed = rss_gen.RSS2(
        title='Feed Title',
        link='http://example.com/link/',
        description='feed description',
        lastBuildDate=now,
        items=[
            rss_gen.RSSItem(
                title='Item Title',
                link='http://example.com/1/',
                description='item description',
                pubDate=now - timedelta(seconds=5),
            ),
            rss_gen.RSSItem(
                title='Second Item Title',
                link='http://example.com/2/',
                description='another item description',
                pubDate=now - timedelta(seconds=10),
            )
        ]
    )
    pseudofile = StringIO()
    feed.write_xml(pseudofile, encoding='utf-8')
    pseudofile.flush()
    pseudofile.seek(0)
    parsed = parse_rss(pseudofile)
    assert_feeds_equal(feed, parsed)


def assert_feeds_equal(f1, f2):
    assert f1.title == f2.title
    assert f1.link == f2.link
    assert f1.description == f2.description
    assert f1.lastBuildDate == f2.lastBuildDate
    assert len(f1.items) == len(f2.items)
    for i1, i2 in zip(f1.items, f2.items):
        assert i1.title == i2.title
        assert i1.link == i2.link
        assert i1.description == i2.description
        assert i1.pubDate == i2.pubDate
