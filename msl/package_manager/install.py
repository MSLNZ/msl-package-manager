"""
Use pip to install MSL repositories from GitHub.
"""
import subprocess

from .helper import _get_packages


def install(names='ALL', yes=False):
    """Use pip to install MSL repositories from GitHub.

    Parameters
    ----------
    names : :obj:`str` or :obj:`list` of :obj:`str`, optional
        The name of a single GitHub repository or a list of repository names. 
        Default is to install **all** MSL packages.

    yes : :obj:`bool`, optional
        Don't ask for confirmation to install. Default is to ask before installing.
    """
    for pkg in _get_packages('install', names, yes):
        subprocess.call(['pip', 'install', 'https://github.com/MSLNZ/{0}/archive/master.zip'.format(pkg)])
