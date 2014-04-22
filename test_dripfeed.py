# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import ConfigParser
from contextlib import contextmanager
import shutil
from datetime import datetime, timedelta
from StringIO import StringIO
from threading import Thread
from time import sleep
import os
import tempfile

from dripfeed import create_comic, run_once
from dripfeed.comics import Comic, XPathComic, Progress, put_comic, _unlocked_get_comic
from dripfeed.rss import parse_rss
import mock
import PyRSS2Gen as rss_gen


@contextmanager
def temp_dir():
    d = tempfile.mkdtemp()
    try:
        yield d
    finally:
        shutil.rmtree(d)


def test_put_config_creates_file():
    with temp_dir() as d:
        fname = os.path.join(d, 'test_config.cfg')
        comic = Comic(name='blah', start_url='http://test.com/',
                      rss_file='/dev/null',
                      progress=Progress(next_url='http://test.com/'))
        with mock.patch('dripfeed.comics.CONF_FILENAME', fname):
            put_comic(comic, create_file=True)

        with open(fname, 'r') as f:
            content = f.read()
        assert content
        assert '[blah]' in content


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
    comic = XPathComic(name='gunnerkrigg',
                       next_xpath="//img[@src='http://www.gunnerkrigg.com/images/next_a.jpg']/..",
                       progress=Progress(next_url='http://gunnerkrigg.com/?p=1'))
    with mock.patch('requests.get', return_value=first_gunnerkrigg_page()):
        next_url = comic.next_url()
    assert next_url == 'http://gunnerkrigg.com/?p=2'


def test_absolute_url():
    # Making sure that the treatment of *relative* URLs still lets *absolute* URLs work if we get those
    comic = comic=XPathComic(name='blah', next_xpath='//a',
                             progress=Progress(next_url='http://base.com/'))
    with mock.patch('requests.get', return_value=mock.Mock()) as get_mock:
        get_mock.return_value.content = '<a href="http://elsewhere.com/">'
        next_url = comic.next_url()
    assert next_url == 'http://elsewhere.com/'


def test_progress_is_optional():
    # Make sure that a Comic() created with progress=None is enough to get started
    comic = XPathComic(name='gunnerkrigg', next_xpath='//a', start_url='http://gunnerkrigg.com/?p=1')
    with mock.patch('requests.get') as get_mock:
        get_mock.return_value.content = '<a href="?p=2"></a>'
        next_url = comic.next_url()
    assert next_url == 'http://gunnerkrigg.com/?p=2'


def test_progress_config_is_optional():
    config_file = StringIO('''
[gunnerkrigg]
long_name = Gunnerkrigg Court
rss_file = /dev/null
start_url = http://gunnerkrigg.com/?p=1
next_xpath = //a
    ''')
    global_config = ConfigParser.SafeConfigParser()
    global_config.readfp(config_file)
    comic = _unlocked_get_comic('gunnerkrigg', global_config)
    with mock.patch('requests.get') as get_mock:
        get_mock.return_value.content = '<a href="?p=2"></a>'
        next_url = comic.next_url()
        comic.update_progress(next_url)
    assert next_url == 'http://gunnerkrigg.com/?p=2'

    with temp_dir() as d:
        fname = os.path.join(d, 'test_config.cfg')
        with mock.patch('dripfeed.comics.CONF_FILENAME', fname):
            put_comic(comic, create_file=True, overwrite=True)

        with open(fname, 'r') as f:
            content = f.read()
        assert content
        assert '[gunnerkrigg]' in content
        assert 'episode = 2' in content
        assert '?p=2' in content


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


def test_init_adds_all_needed_data():
    with temp_dir() as d:
        conf_fname = os.path.join(d, 'test_config.cfg')
        rss_fname = os.path.join(d, 'test.rss')
        with mock.patch('dripfeed.comics.CONF_FILENAME', conf_fname):
            create_comic('gunnerkrigg', rss_fname, '//a', 'http://gunnerkrigg.com/?p=1')
            with mock.patch('requests.get') as get_mock:
                get_mock.return_value.content = '<a href="?p=2"></a>'
                run_once('gunnerkrigg')

        with open(conf_fname, 'r') as f:
            content = f.read()
        assert content
        assert '[gunnerkrigg]' in content
        assert 'episode = 2' in content
        assert '?p=2' in content
        with open(rss_fname, 'r') as f:
            content = f.read()
        assert content
        assert 'Episode 0' not in content
        assert 'Episode 1' in content
        assert 'Episode 2' in content
        assert 'http://gunnerkrigg.com/?p=1' in content
        assert 'http://gunnerkrigg.com/?p=2' in content


def test_file_locking():
    with temp_dir() as d:
        conf_fname = os.path.join(d, 'test_config.cfg')
        with open(conf_fname, 'w') as f:
            f.writelines([b'[default]'])

        # Wrap comic.add_to_global_config() to pause before writing: this is called *after* the read, so will guarantee
        # a write collision if locking is not set up correctly.
        orig_add_to_global_config = Comic.add_to_global_config
        def patched_add_to_global_config(*args, **kwargs):
            sleep(1)
            orig_add_to_global_config(*args, **kwargs)

        try:  # monkey-patching :-/

            Comic.add_to_global_config = patched_add_to_global_config

            def add_comic(name):
                comic = XPathComic(name=name, start_url='http://test.com/', rss_file='test.rss', next_xpath='//a')
                with mock.patch('dripfeed.comics.CONF_FILENAME', conf_fname):
                    put_comic(comic)

            t1 = Thread(target=add_comic, args=('gunnerkrigg',))
            t2 = Thread(target=add_comic, args=('narbonic',))

            t1.start()
            t2.start()

            t1.join()
            t2.join()

        finally:
            Comic.add_to_global_config = orig_add_to_global_config

        with open(conf_fname, 'r') as f:
            content = f.read()
        assert '[narbonic]' in content
        assert '[gunnerkrigg]' in content
    