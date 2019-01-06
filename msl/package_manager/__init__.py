"""
Install, uninstall, update, list and create MSL packages.

The following constants are available.
"""
import re
from collections import namedtuple

__author__ = 'Joseph Borbely'
__copyright__ = '\xa9 2017 - 2019, ' + __author__
__version__ = '2.2.1.dev0'

_v = re.search(r'(\d+)\.(\d+)\.(\d+)[.-]?(.*)', __version__).groups()

version_info = namedtuple('version_info', 'major minor micro releaselevel')(int(_v[0]), int(_v[1]), int(_v[2]), _v[3])
""":obj:`~collections.namedtuple`: Contains the version information as a (major, minor, micro, releaselevel) tuple."""

_PKG_NAME = 'msl-package-manager'

from .utils import pypi
from .utils import github
from .utils import installed
from .utils import info
from .utils import set_log_level
from .update import update
from .create import create
from .install import install
from .uninstall import uninstall
