"""
Install, uninstall, update, list and create MSL packages.

The following constants are available.
"""
from collections import namedtuple

__author__ = 'Joseph Borbely'
__copyright__ = '\xa9 2017 - 2018, ' + __author__
__version__ = '1.5.2.dev0'

version_info = namedtuple('version_info', 'major minor micro')(*map(int, __version__.split('.')[:3]))
""":obj:`~collections.namedtuple`: Contains the version information as a (major, minor, micro) tuple."""

PKG_NAME = 'msl-package-manager'
""":class:`str`: The name of this package when it is installed"""

from .utils import pypi
from .utils import github
from .utils import installed
from .utils import show_packages
from .utils import set_log_level
from .update import update
from .create import create
from .install import install
from .uninstall import uninstall
