import sys
import time
from collections import namedtuple

from colorama import init
init(autoreset=True)

version_info = namedtuple('version_info', 'major minor micro releaselevel')(0, 1, 0, 'beta')
""":func:`~collections.namedtuple`: Contains the version information as a (major, minor, micro, releaselevel) tuple."""

__author__ = 'Joseph Borbely'
__copyright__ = '\xa9 2017{}, {}'.format(time.strftime('-%Y') if int(time.strftime('%Y')) > 2017 else '', __author__)
__version__ = '{}.{}.{}'.format(*version_info)

PKG_NAME = 'msl-package-manager'
IS_PYTHON2 = sys.version_info[0] == 2
IS_PYTHON3 = sys.version_info[0] == 3

from msl.package_manager.helper import *
from msl.package_manager.create import create
