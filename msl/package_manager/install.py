"""
Install MSL repositories_ from GitHub.

.. _repositories: https://github.com/MSLNZ
"""
import sys
import subprocess

from . import helper


def install(names=None, yes=False, update_github_cache=False, branch=None, tag=None):
    """Install MSL repositories_ from GitHub.

    .. _repositories: https://github.com/MSLNZ

    Parameters
    ----------
    names : :obj:`str` or :obj:`list` of :obj:`str`, optional
        The name of a single GitHub `repository <repositories_>`_ or a list of
        `repository <repositories_>`_ names.
        If :obj:`None` then install **all** MSL packages.
    yes : :obj:`bool`, optional
        If :obj:`True` then don't ask for confirmation before installing.
        The default is to ask before installing.
    update_github_cache : :obj:`bool`, optional
        The information about the repositories_ that are available on GitHub are
        cached to use for subsequent calls to this function. After 24 hours the
        cache is automatically updated. Set `update_github_cache` to be :obj:`True`
        to force the cache to be updated when you call this function.
    branch : :obj:`str`, optional
        The name of a GitHub branch to use for the installation. If :obj:`None`
        and no `tag` value has been specified then installs from the **master** branch.
    tag : :obj:`str`, optional
        The name of a GitHub tag to use for the installation.

        .. attention::
           Cannot specify both a `branch` and a `tag` simultaneously.
    """
    zip_name = helper.get_zip_name(branch, tag)
    if zip_name is None:
        return

    packages = helper.create_install_list(names, branch, tag, update_github_cache)
    if not packages:
        print('No MSL packages to install')
        return

    helper.print_install_uninstall_message(packages, 'INSTALLED', branch, tag)
    if not (yes or helper.ask_proceed()):
        return

    print('')
    exe = [sys.executable, '-m', 'pip', 'install']
    options = ['--process-dependency-links']
    for pkg in packages:
        repo = ['https://github.com/MSLNZ/{}/archive/{}.zip'.format(pkg, zip_name)]
        subprocess.call(exe + options + repo)
