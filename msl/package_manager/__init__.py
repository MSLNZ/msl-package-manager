import time
from collections import namedtuple

version_info = namedtuple('version_info', 'major minor micro releaselevel')(0, 1, 0, 'beta')
""":func:`~collections.namedtuple`: Contains the version information as a (major, minor, micro, releaselevel) tuple."""

__author__ = 'Joseph Borbely'
__copyright__ = '\xa9 2017{}, {}'.format(time.strftime('-%Y') if int(time.strftime('%Y')) > 2017 else '', __author__)
__version__ = '{}.{}.{}'.format(*version_info)

NAME = 'msl-package-manager'

from .main import *
