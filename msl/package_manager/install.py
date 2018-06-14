"""
Install MSL packages.
"""
import sys
import subprocess

from . import helper


def install(names=None, yes=False, branch=None, tag=None, update_cache=False):
    """Install MSL packages.

    MSL packages can be installed from PyPI packages_ (only if a release has been
    uploaded to PyPI_) or from GitHub repositories_.

    .. note::
       If the MSL packages_ are available on PyPI_ then PyPI_ is used as the default
       URI_ to install the package. If you want to force the installation to occur
       from the ``master`` branch of the GitHub `repository <https://github.com/MSLNZ>`_
       then set ``branch = 'master'``. If the package is not available on PyPI_
       then the ``master`` branch is used as the default installation URI_.

    .. _repositories: https://github.com/MSLNZ
    .. _packages: https://pypi.org/search/?q=msl-*
    .. _PyPI: https://pypi.org/
    .. _URI: https://en.wikipedia.org/wiki/Uniform_Resource_Identifier

    Parameters
    ----------
    names : :class:`str` or :class:`list` of :class:`str`, optional
        The name(s) of the MSL package(s) to install. If :obj:`None` then
        install **all** MSL packages.
    yes : :class:`bool`, optional
        If :obj:`True` then don't ask for confirmation before installing.
        The default is to ask before installing.
    branch : :class:`str`, optional
        The name of a GitHub branch to use for the installation. If :obj:`None`
        and no `tag` value has been specified then installs from the ``master``
        branch.
    tag : :class:`str`, optional
        The name of a GitHub tag to use for the installation.
    update_cache : :class:`bool`, optional
        The information about the MSL packages_ that are available on PyPI_ and about
        the repositories_ that are available on GitHub are cached to use for subsequent
        calls to this function. After 24 hours the cache is automatically updated. Set
        `update_cache` to be :obj:`True` to force the cache to be updated when you call
        this function.

        .. attention::
           Cannot specify both a `branch` and a `tag` simultaneously.
    """
    zip_name = helper.get_zip_name(branch, tag)
    if zip_name is None:
        return

    packages = helper.create_install_list(names, branch, tag, update_cache)
    if not packages:
        print('No MSL packages to install')
        return

    pkgs_pypi = helper.pypi(update_cache)

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
