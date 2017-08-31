"""
Use pip to install MSL repositories_ from GitHub.

.. _repositories: https://github.com/MSLNZ
"""
import sys
import subprocess

from .helper import _get_packages


def install(names='ALL', yes=False, update_github_cache=False):
    """Use pip to install MSL repositories_ from GitHub.

    .. _repositories: https://github.com/MSLNZ

    Parameters
    ----------
    names : :obj:`str` or :obj:`list` of :obj:`str`, optional
        The name of a single GitHub `repository <repositories_>`_ or a list of
        `repository <repositories_>`_ names.
        Default is to install **all** MSL packages.
    yes : :obj:`bool`, optional
        Don't ask for confirmation to install. Default is to ask before installing.
    update_github_cache : :obj:`bool`, optional
        The information about the repositories_ that are available on GitHub are
        cached to use for subsequent calls to this function. After 24 hours the
        cache is automatically updated. Set `update_github_cache` to be :obj:`True`
        to force the cache to be updated when you call this function.
    """
    for pkg in _get_packages('install', names, yes, update_github_cache):
        repo = 'https://github.com/MSLNZ/{0}/archive/master.zip'.format(pkg)
        subprocess.call([sys.executable, '-m', 'pip', 'install', repo, '--process-dependency-links'])
