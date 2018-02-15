"""
Install MSL packages.
"""
import sys
import subprocess

from . import helper


def install(names=None, yes=False, update_github_cache=False, branch=None, tag=None, update_pypi_cache=False):
    """Install MSL packages.

    .. _MSL repositories: https://github.com/MSLNZ
    .. _MSL packages: https://pypi.org/search/?q=msl-*
    .. _PyPI: https://pypi.org/

    Parameters
    ----------
    names : :obj:`str` or :obj:`list` of :obj:`str`, optional
        The name(s) of the MSL package(s) to install. If :obj:`None` then
        install **all** MSL packages.
    yes : :obj:`bool`, optional
        If :obj:`True` then don't ask for confirmation before installing.
        The default is to ask before installing.
    update_github_cache : :obj:`bool`, optional
        The information about the `MSL repositories`_ that are available on GitHub
        are cached to use for subsequent calls to this function. After 24 hours the
        cache is automatically updated. Set `update_github_cache` to be :obj:`True`
        to force the cache to be updated when you call this function.
    branch : :obj:`str`, optional
        The name of a GitHub branch to use for the installation. If :obj:`None`
        and no `tag` value has been specified then installs from the **master** branch.
    tag : :obj:`str`, optional
        The name of a GitHub tag to use for the installation.
    update_pypi_cache : :obj:`bool`, optional
        The information about the `MSL packages`_ that are available on PyPI_ are
        cached to use for subsequent calls to this function. After 24 hours the
        cache is automatically updated. Set `update_pypi_cache` to be :obj:`True`
        to force the cache to be updated when you call this function.

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

    pkgs_pypi = helper.pypi(update_pypi_cache)

    helper.print_install_uninstall_message(packages, 'INSTALLED', branch, tag)
    if not (yes or helper.ask_proceed()):
        return

    print('')
    exe = [sys.executable, '-m', 'pip', 'install']
    github_options = ['--process-dependency-links']
    for pkg in packages:
        if pkg in pkgs_pypi and branch is None and tag is None:
            # install the package from PyPI
            subprocess.call(exe + [pkg])
        else:
            repo = ['https://github.com/MSLNZ/{}/archive/{}.zip'.format(pkg, zip_name)]
            subprocess.call(exe + github_options + repo)
