"""
Use pip to install MSL repositories_ from GitHub.

.. _repositories: https://github.com/MSLNZ
"""
import sys
import subprocess

from .helper import _get_packages, _get_zip_name


def install(names='ALL', yes=False, update_github_cache=False, branch=None, tag=None):
    """Use pip to install MSL repositories_ from GitHub.

    .. _repositories: https://github.com/MSLNZ

    Parameters
    ----------
    names : :obj:`str` or :obj:`list` of :obj:`str`, optional
        The name of a single GitHub `repository <repositories_>`_ or a list of
        `repository <repositories_>`_ names.
        Default is to install **all** MSL packages.
    yes : :obj:`bool`, optional
        If :obj:`True` then don't ask for confirmation to install.
        Default is to ask before installing.
    update_github_cache : :obj:`bool`, optional
        The information about the repositories_ that are available on GitHub are
        cached to use for subsequent calls to this function. After 24 hours the
        cache is automatically updated. Set `update_github_cache` to be :obj:`True`
        to force the cache to be updated when you call this function.
    branch : :obj:`str`, optional
        The name of a GitHub branch to install. If :obj:`None` and no
        `tag` value has been specified then installs the **master** branch.
    tag : :obj:`str`, optional
        The name of a GitHub tag to use for the install.

    .. note::
       Cannot specify both a `branch` and a `tag`.
    """
    zip_name = _get_zip_name(branch, tag)
    if zip_name is None:
        return

    exe = [sys.executable, '-m', 'pip', 'install']
    options = ['--process-dependency-links']
    for pkg in _get_packages('install', names, yes, update_github_cache, branch, tag):
        repo = ['https://github.com/MSLNZ/{}/archive/{}.zip'.format(pkg, zip_name)]
        subprocess.call(exe + options + repo)
