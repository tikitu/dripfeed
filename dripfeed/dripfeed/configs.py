import contextlib

__author__ = 'tikitu'


@contextlib.contextmanager
def locked_config():
    yield
    raise NotImplementedError()


def get_config(comic_name):
    with locked_config():
        raise NotImplementedError()


def put_config(comic_name):
    with locked_config():
        raise NotImplementedError()


