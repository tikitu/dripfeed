import six

__author__ = 'tikitu'


if six.PY3:
    from configparser import ConfigParser
else:
    from ConfigParser import SafeConfigParser as ConfigParser
    ConfigParser.read_file = ConfigParser.readfp

from six.moves.urllib.parse import urljoin

