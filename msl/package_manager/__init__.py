"""
Allows you to install, uninstall, list and create MSL packages.
"""
import sys
import time
from collections import namedtuple

version_info = namedtuple('version_info', 'major minor micro releaselevel')(0, 1, 0, 'beta')
""":func:`~collections.namedtuple`: Contains the version information as a (major, minor, micro, releaselevel) tuple."""

__author__ = 'Joseph Borbely'
__copyright__ = '\xa9 2017{}, {}'.format(time.strftime('-%Y') if int(time.strftime('%Y')) > 2017 else '', __author__)
__version__ = '{}.{}.{}'.format(*version_info)

PKG_NAME = 'msl-package-manager'
""":class:`str`: The name of the package when it is installed"""

IS_PYTHON2 = sys.version_info[0] == 2
""":class:`bool`: Whether Python 2.x is being used."""

IS_PYTHON3 = sys.version_info[0] == 3
""":class:`bool`: Whether Python 3.x is being used."""

try:
    from colorama import init
    init(autoreset=True)

    from msl.package_manager.helper import *
    from msl.package_manager.create import create

except ImportError:
    # when running setup.py the colorama package might not be installed yet but the
    # setup.py script only needs the value of __author__ and __version__ when it is called
    # because colorama will be installed when it is needed
    pass
