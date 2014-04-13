import contextlib
import os
import simplejson as json
import portalocker

__author__ = 'tikitu'


class Config(object):

    FILENAME = '~/dripfeed.cfg'

    def __init__(self, comic_name=None, downloaded_count=0, next_url=None):
        self.comic_name = comic_name
        self.downloaded_count = downloaded_count
        self.next_url = next_url

    def as_json_d(self):
        """Return a dict suitable for updating the global config dict: global.update(a_config.as_json_d())."""
        return {
            self.comic_name: {
                'downloaded_count': self.downloaded_count,
                'next_url': self.next_url,
            }
        }


@contextlib.contextmanager
def locked_config_file(filename=Config.FILENAME):
    """
    Get and release lock on global config file.
    We use this whenever reading/writing (but *not* over whole program run!).
    This locking pattern makes it safe to run multiple instances concurrently, so long as they don't update the same
    comic: update Gunnerkrigg Court daily and Narbonic hourly with separate cron jobs (but don't update Narbonic hourly
    *and* daily, although why would you want to?).
    """
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


def get_config(comic_name):
    with locked_config_file() as f:
        global_config = json.load(f)
        return Config(comic_name=comic_name, **global_config.get(comic_name, {}))


def put_config(config, create_file=False, filename=Config.FILENAME):
    # NOT under locking: there's no (sane) way to lock file creation safely :-/ So be careful when you call this!
    if create_file and not os.path.isfile(filename):
        with open(filename, 'w+') as f:
            f.write('{}')
            f.write(os.linesep)
    with locked_config_file(filename=filename) as f:
        global_config = json.load(f)
        global_config.update(config.as_json_d())
        f.seek(0)
        json.dump(global_config, f)



