"""
Use pip to uninstall MSL packages.
"""
import sys
import subprocess

from .helper import _get_packages


def uninstall(names='ALL', yes=False):
    """Use pip to uninstall MSL packages.

    Parameters
    ----------
    names : :obj:`str` or :obj:`list` of :obj:`str`, optional
        The name of a single MSL package or a list of MSL package names to uninstall. 
        Default is to uninstall all MSL packages (except for the **msl-package-manager**).

    yes : :obj:`bool`, optional
        Don't ask for confirmation to uninstall. Default is to ask before uninstalling.
    """
    for pkg in _get_packages('uninstall', names, yes):
        subprocess.call([sys.executable, '-m', 'pip', 'uninstall', '-y', pkg])
