"""
Allows you to install, uninstall, list and create MSL packages.
"""
import sys
from collections import namedtuple
from colorama import init

__author__ = 'Joseph Borbely'
__copyright__ = '\xa9 2017, ' + __author__
__version__ = '0.1.0'

version_info = namedtuple('version_info', 'major minor micro')(*map(int, __version__.split('.')))
""":func:`~collections.namedtuple`: Contains the version information as a (major, minor, micro) tuple."""

PKG_NAME = 'msl-package-manager'
""":class:`str`: The name of the package when it is installed"""

IS_PYTHON2 = sys.version_info[0] == 2
""":class:`bool`: Whether Python 2.x is being used."""

IS_PYTHON3 = sys.version_info[0] == 3
""":class:`bool`: Whether Python 3.x is being used."""

from .helper import *
from .create import create
from .install import install
from .uninstall import uninstall

init(autoreset=True)
