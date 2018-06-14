"""
Update MSL packages.
"""
import sys
import subprocess
from pkg_resources import parse_version

from colorama import Fore

from . import PKG_NAME, helper


def update(names=None, yes=False, update_github_cache=False, branch=None, tag=None, update_pypi_cache=False):
    """Update MSL packages.

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
        The name(s) of the MSL package(s) to update. The default is to update
        **all** MSL packages (except for the **MSL Package Manager** -- use ``pip``).
    yes : :class:`bool`, optional
        If :obj:`True` then don't ask for confirmation before updating.
        The default is to ask before updating.
    update_github_cache : :class:`bool`, optional
        The information about the repositories_ that are available on GitHub are
        cached to use for subsequent calls to this function. After 24 hours the
        cache is automatically updated. Set `update_github_cache` to be :obj:`True`
        to force the cache to be updated when you call this function.
    branch : :class:`str`, optional
        The name of a GitHub branch to use for the update. If :obj:`None`, and no
        `tag` value has also been specified, then updates the package using the
        ``master`` branch.
    tag : :class:`str`, optional
        The name of a GitHub tag to use for the update.
    update_pypi_cache : :class:`bool`, optional
        The information about the MSL packages_ that are available on PyPI_ are
        cached to use for subsequent calls to this function. After 24 hours the
        cache is automatically updated. Set `update_pypi_cache` to be :obj:`True`
        to force the cache to be updated when you call this function.

        .. attention::
           Cannot specify both a `branch` and a `tag` simultaneously.

        .. important::
           If you specify a `branch` or a `tag` then the update will be forced.
    """
    zip_name = helper.get_zip_name(branch, tag)
    if zip_name is None:
        return

    pkgs_github = helper.github(update_github_cache)
    pkgs_pypi = helper.pypi(update_pypi_cache)
    if not pkgs_github and not pkgs_pypi:
        return

    pkgs_installed = helper.installed()

    names = helper.check_msl_prefix(names)
    if not names:
        names = [pkg for pkg in pkgs_installed if pkg != PKG_NAME]
    elif PKG_NAME in names:
        helper.print_warning('Use "pip install {} --upgrade" to update the MSL Package Manager'.format(PKG_NAME))
        del names[names.index(PKG_NAME)]

    w = [0, 0]
    pkgs_to_update = {}
    for name in names:

        err_msg = 'Cannot update {}: '.format(name)

        if name not in pkgs_installed:
            helper.print_error(err_msg + 'package not installed')
            continue

        if name not in pkgs_github and name not in pkgs_pypi:
            helper.print_error(err_msg + 'package not found on GitHub or PyPI')
            continue

        installed_version = pkgs_installed[name]['version']

        # use PyPI to update the package (only if the package is available on PyPI)
        using_pypi = name in pkgs_pypi and tag is None and branch is None

        if tag is not None:
            if tag in pkgs_github[name]['tags']:
                pkgs_to_update[name] = (installed_version, '[tag:{}]'.format(tag), using_pypi)
            else:
                helper.print_error(err_msg + 'a "{}" tag does not exist'.format(tag))
                continue
        elif branch is not None:
            if branch in pkgs_github[name]['branches']:
                pkgs_to_update[name] = (installed_version, '[branch:{}]'.format(branch), using_pypi)
            else:
                helper.print_error(err_msg + 'a "{}" branch does not exist'.format(branch))
                continue
        else:
            if using_pypi:
                version = pkgs_pypi[name]['version']
            else:
                version = pkgs_github[name]['version']

            if not version:
                # a version number must exist on PyPI, so if this occurs it must be for a github repo
                helper.print_error(err_msg + 'the github repository does not contain a release')
                continue
            elif parse_version(version) > parse_version(installed_version):
                pkgs_to_update[name] = (installed_version, version, using_pypi)
            else:
                helper.print_warning('The {} package is already the latest [{}]'.format(name, installed_version))
                continue

        w = [max(w[0], len(name)), max(w[1], len(installed_version))]

    if pkgs_to_update:
        pkgs_to_update = helper.sort_packages(pkgs_to_update)

        msg = '\nThe following MSL packages will be {}UPDATED{}:\n'.format(Fore.CYAN, Fore.RESET)
        for pkg in pkgs_to_update:
            local, remote, _ = pkgs_to_update[pkg]
            pkg += ': '
            msg += '\n  ' + pkg.ljust(w[0]+2) + local.ljust(w[1]) + ' --> ' + remote

        print(msg)
        if not (yes or helper.ask_proceed()):
            return
        print('')

        exe = [sys.executable, '-m', 'pip', 'install']
        options = ['--upgrade', '--force-reinstall', '--no-deps']
        for pkg in pkgs_to_update:
            if pkgs_to_update[pkg][2]:
                package = [pkg]  # update from PyPI
            else:
                package = ['https://github.com/MSLNZ/{}/archive/{}.zip'.format(pkg, zip_name)]
            subprocess.call(exe + options + package)
    else:
        print('No MSL packages to update')
