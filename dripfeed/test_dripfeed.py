# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import shutil
import os
from subprocess import check_output
import tempfile
from dripfeed.configs import put_config, Config
import simplejson as json


def test_put_config_creates_file():
    d = tempfile.mkdtemp()
    try:
        fname = os.path.join(d, 'test_config.cfg')
        config = Config(comic_name='blah', downloaded_count=0, next_url='http://test.com/')
        put_config(config, create_file=True, filename=fname)

        with open(fname, 'r') as f:
            content = f.read()
        assert content
        content = json.loads(content)
        assert 'blah' in content
        assert content['blah']
    finally:
        shutil.rmtree(d)