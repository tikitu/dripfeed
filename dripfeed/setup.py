# -*- coding: utf-8 -*-
import re
import sys
from setuptools import setup
from setuptools.command.test import test as TestCommand


REQUIRES = [
    'docopt',
    'simplejson',
    'portalocker',
    'requests',
    'lxml',
]

class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest
        errcode = pytest.main(self.test_args)
        sys.exit(errcode)


def find_version(fname):
    '''Attempts to find the version number in the file names fname.
    Raises RuntimeError if not found.
    '''
    version = ''
    with open(fname, 'r') as fp:
        reg = re.compile(r'__version__ = [\'"]([^\'"]*)[\'"]')
        for line in fp:
            m = reg.match(line)
            if m:
                version = m.group(1)
                break
    if not version:
        raise RuntimeError('Cannot find version information')
    return version

__version__ = find_version("dripfeed/__init__.py")


def read(fname):
    with open(fname) as fp:
        content = fp.read()
    return content

setup(
    name='dripfeed',
    version="0.1.0",
    description='Create an RSS feed of a webcomic archive, for slow perusal.',
    long_description=read("README.rst"),
    author='Tikitu de Jager',
    author_email='tikitu@logophile.org',
    url='https://bitbucket.org/tikitu/dripfeed',
    install_requires=REQUIRES,
    license=read("LICENSE"),
    zip_safe=False,
    keywords='dripfeed',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy'
    ],
    packages=["dripfeed"],
    entry_points={
        'console_scripts': [
            "dripfeed = dripfeed:main"
        ]
    },
    tests_require=[
        'pytest',
        'simplejson',
    ],
    cmdclass={'test': PyTest}
)