import six

__author__ = 'tikitu'


if six.PY2:
    from ConfigParser import SafeConfigParser as ConfigParser
    ConfigParser.read_file = ConfigParser.readfp
else:
    from configparser import ConfigParser

from six.moves.urllib.parse import urljoin

