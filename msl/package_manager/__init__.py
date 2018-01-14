"""
Install, uninstall, update, list and create MSL packages.

The following constants are available.
"""
import sys
from collections import namedtuple

__author__ = 'Joseph Borbely'
__copyright__ = '\xa9 2017 - 2018, ' + __author__
__version__ = '1.4.2.dev0'

version_info = namedtuple('version_info', 'major minor micro')(*map(int, __version__.split('.')[:3]))
""":obj:`~collections.namedtuple`: Contains the version information as a (major, minor, micro) tuple."""

PKG_NAME = 'msl-package-manager'
""":obj:`str`: The name of this package when it is installed"""

IS_PYTHON2 = sys.version_info[0] == 2
""":obj:`bool`: Whether Python 2.x is being used."""

IS_PYTHON3 = sys.version_info[0] == 3
""":obj:`bool`: Whether Python 3.x is being used."""

from .helper import installed
from .helper import github
from .create import create
from .install import install
from .uninstall import uninstall
from .update import update
from .print_packages import print_packages

import colorama
colorama.init(autoreset=True)
