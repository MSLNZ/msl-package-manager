"""
Install, uninstall, update, list and create MSL packages.

The following constants are available.
"""
import re
from collections import namedtuple

from .authorise import authorise
from .create import create
from .install import install
from .uninstall import uninstall
from .update import update
from .utils import github
from .utils import info
from .utils import installed
from .utils import outdated_pypi_packages
from .utils import pypi
from .utils import set_log_level

__author__ = 'Measurement Standards Laboratory of New Zealand'
__copyright__ = '\xa9 2017 - 2023, ' + __author__
__version__ = '2.5.4'

_v = re.search(r'(\d+)\.(\d+)\.(\d+)[.-]?(.*)', __version__).groups()

version_info = namedtuple('version_info', 'major minor micro releaselevel')(int(_v[0]), int(_v[1]), int(_v[2]), 'final')
""":obj:`~collections.namedtuple`: Contains the version information as a (major, minor, micro, releaselevel) tuple."""
