"""
Use pip to install MSL repositories from GitHub.
"""
import sys
import subprocess

from .helper import _get_packages


def install(names='ALL', yes=False, get_release_version=False):
    """Use pip to install MSL repositories from GitHub.

    Parameters
    ----------
    names : :obj:`str` or :obj:`list` of :obj:`str`, optional
        The name of a single GitHub repository or a list of repository names. 
        Default is to install **all** MSL packages.

    yes : :obj:`bool`, optional
        Don't ask for confirmation to install. Default is to ask before installing.
    
    get_release_version : :obj:`bool`, optional
        Get the latest release version information. Getting the release version 
        will make this function take longer to finish. Also, the repository might
        not have published a release tag so the release information might not be 
        available. Default is :obj:`False`.
    """
    for pkg in _get_packages('install', names, yes, get_release_version=get_release_version):
        repo = 'https://github.com/MSLNZ/{0}/archive/master.zip'.format(pkg)
        subprocess.call([sys.executable, '-m', 'pip', 'install', repo, '--process-dependency-links'])
