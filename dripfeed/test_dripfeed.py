# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import shutil
from dripfeed.comics import Comic
import os
import tempfile
from dripfeed.configs import put_config, Config


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