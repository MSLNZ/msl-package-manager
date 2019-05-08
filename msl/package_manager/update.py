"""
Update MSL packages.
"""
import os
import sys
import subprocess
from pkg_resources import parse_version

from colorama import Fore

from . import utils, _PKG_NAME


def update(*names, **kwargs):
    """Update MSL packages.

    MSL packages can be updated from PyPI packages_ (only if a release has been
    uploaded to PyPI) or from GitHub repositories_.

    .. note::
       If the MSL packages_ are available on PyPI then PyPI is used as the default
       URI_ to update the package. If you want to force the update to occur
       from the ``master`` branch of the GitHub `repository <https://github.com/MSLNZ>`_
       then set ``branch='master'``. If the package is not available on PyPI
       then the ``master`` branch is used as the default update URI_.

    .. _repositories: https://github.com/MSLNZ
    .. _packages: https://pypi.org/search/?q=%22Measurement+Standards+Laboratory+of+New+Zealand%22
    .. _URI: https://en.wikipedia.org/wiki/Uniform_Resource_Identifier

    Parameters
    ----------
    *names : :class:`str`
        The name(s) of the MSL package(s) to update. If not specified then
        update all MSL packages. The ``msl-`` prefix can be omitted (e.g.,
        ``'loadlib'`` is equivalent to ``'msl-loadlib'``). Also accepts
        shell-style wildcards (e.g., ``'pr-*'``).
    **kwargs
        * branch : :class:`str`
            The name of a GitHub branch to use for the update. If :data:`None`, and no
            `tag` value has also been specified, then updates the package using the
            ``master`` branch. Default is :data:`None`.
        * tag : :class:`str`
            The name of a GitHub tag to use for the update. Default is :data:`None`.
        * update_cache : :class:`bool`
            The information about the MSL packages_ that are available on PyPI and about
            the repositories_ that are available on GitHub are cached to use for subsequent
            calls to this function. After 24 hours the cache is automatically updated. Set
            `update_cache` to be :data:`True` to force the cache to be updated when you call
            this function. Default is :data:`False`.
        * yes : :class:`bool`
            If :data:`True` then don't ask for confirmation before updating.
            The default is :data:`False` (ask before updating).

        .. attention::
           Cannot specify both a `branch` and a `tag` simultaneously.

        .. important::
           If you specify a `branch` or a `tag` then the update will be forced.
    """
    # Python 2.7 does not support named arguments after using *args
    # we can define yes=False, branch=None, tag=None, update_cache=False in the function signature
    # if we choose to drop support for Python 2.7
    utils._check_kwargs(kwargs, {'yes', 'branch', 'tag', 'update_cache'})

    yes = kwargs.get('yes', False)
    branch = kwargs.get('branch', None)
    tag = kwargs.get('tag', None)
    update_cache = kwargs.get('update_cache', False)

    zip_name = utils._get_github_zip_name(branch, tag)
    if zip_name is None:
        return

    pkgs_installed = utils.installed()
    pkgs_github = utils.github(update_cache=update_cache)
    pkgs_pypi = utils.pypi(update_cache=update_cache)
    if not pkgs_github and not pkgs_pypi:
        return

    if not names:
        names = pkgs_installed.keys()  # update all installed packages
    else:
        names = utils._check_wildcards_and_prefix(names, pkgs_installed)

    w = [0, 0]
    pkgs_to_update = dict()
    for name in names:

        err_msg = 'Cannot update {!r}. '.format(name)

        if name not in pkgs_installed:
            utils.log.error(err_msg + 'The package is not installed.')
            continue

        installed_version = pkgs_installed[name]['version']

        # use PyPI to update the package (only if the package is available on PyPI)
        using_pypi = name in pkgs_pypi and tag is None and branch is None
        repo_name = pkgs_installed[name]['repo_name']

        if tag is not None:
            if tag in pkgs_github[repo_name]['tags']:
                pkgs_to_update[name] = (installed_version, '[tag:{}]'.format(tag), using_pypi)
            else:
                utils.log.error(err_msg + 'A {!r} tag does not exist.'.format(tag))
                continue
        elif branch is not None:
            if branch in pkgs_github[repo_name]['branches']:
                pkgs_to_update[name] = (installed_version, '[branch:{}]'.format(branch), using_pypi)
            else:
                utils.log.error(err_msg + 'A {!r} branch does not exist.'.format(branch))
                continue
        else:
            if using_pypi:
                version = pkgs_pypi[name]['version']
            else:
                version = pkgs_github[repo_name]['version']

            if not version:
                # a version number must exist on PyPI, so if this occurs it must be for a github repo
                utils.log.error(err_msg + 'The GitHub repository does not contain a release.')
                continue
            elif parse_version(version) > parse_version(installed_version):
                pkgs_to_update[name] = (installed_version, version, using_pypi)
            else:
                utils.log.warning('The {!r} package is already the latest [{}]'.format(name, installed_version))
                continue

        w = [max(w[0], len(name)), max(w[1], len(installed_version))]

    if pkgs_to_update:
        pkgs_to_update = utils._sort_packages(pkgs_to_update)

        msg = '\n{}The following MSL packages will be {}UPDATED{}:\n'.format(Fore.RESET, Fore.CYAN, Fore.RESET)
        for pkg in pkgs_to_update:
            local, remote, _ = pkgs_to_update[pkg]
            pkg += ': '
            msg += '\n  ' + pkg.ljust(w[0]+2) + local.ljust(w[1]) + ' --> ' + remote

        utils.log.info(msg)
        if not (yes or utils._ask_proceed()):
            return

        utils.log.info('')

        # If updating the msl-package-manager then update it last
        updating_msl_package_manager = _PKG_NAME in pkgs_to_update
        if updating_msl_package_manager:
            value = pkgs_to_update.pop(_PKG_NAME)
            pkgs_to_update[_PKG_NAME] = value  # using an OrderedDict so this item will be last

        exe = [sys.executable, '-m', 'pip', 'install']
        options = ['--disable-pip-version-check', '--upgrade', '--force-reinstall', '--no-deps']
        options += ['--quiet'] * utils._NUM_QUIET
        for pkg in pkgs_to_update:
            if pkgs_to_update[pkg][2]:
                utils.log.debug('Updating {!r} from PyPI'.format(pkg))
                package = [pkg]
            else:
                utils.log.debug('Updating {!r} from GitHub/{}'.format(pkg, zip_name))
                package = ['https://github.com/MSLNZ/{}/archive/{}.zip'.format(pkg, zip_name)]

            if utils._IS_WINDOWS and pkg == _PKG_NAME:
                # On Windows, an executable cannot replace itself while it is running. However,
                # an executable can be renamed while it is running. Therefore, we rename msl.exe
                # to msl.exe.old and then a new msl.exe file can be created during the update
                filename = sys.exec_prefix + '/Scripts/msl.exe'
                os.rename(filename, filename + '.old')

            subprocess.call(exe + options + package)

        if updating_msl_package_manager:
            return 'updating_msl_package_manager'

    else:
        utils.log.info('No MSL packages to update.')
