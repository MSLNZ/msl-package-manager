"""
Use pip to update MSL packages.
"""
import sys
import subprocess
from pkg_resources import parse_version

from colorama import Fore, Style

from . import PKG_NAME
from .helper import github, installed, _get_names, _ask_proceed, _sort_packages, _get_zip_name


def update(names='ALL', yes=False, update_github_cache=False, branch=None, tag=None):
    """Use pip to update MSL packages.

    .. _repositories: https://github.com/MSLNZ

    Parameters
    ----------
    names : :obj:`str` or :obj:`list` of :obj:`str`, optional
        The name(s) of MSL package(s) to update. Default is to update **all** MSL
        packages (except for the **MSL Package Manager**).
    yes : :obj:`bool`, optional
        If :obj:`True` then don't ask for confirmation to install.
        Default is to ask before updating.
    update_github_cache : :obj:`bool`, optional
        The information about the repositories_ that are available on GitHub are
        cached to use for subsequent calls to this function. After 24 hours the
        cache is automatically updated. Set `update_github_cache` to be :obj:`True`
        to force the cache to be updated when you call this function.
    branch : :obj:`str`, optional
        The name of a GitHub branch to use for the update. If :obj:`None`, and no
        `tag` value has also been specified, then updates the package using the
        **master** branch.
    tag : :obj:`str`, optional
        The name of a GitHub tag to use for the update.

    .. note::
       Cannot specify both a `branch` and a `tag`. If you specify a `branch` or a `tag`
       then the update will be forced.
    """
    zip_name = _get_zip_name(branch, tag)
    if zip_name is None:
        return

    pkgs_github = github(update_github_cache)
    if not pkgs_github:
        return
    pkgs_installed = installed()

    pkgs = _get_names(names)
    if not pkgs:
        pkgs = [pkg for pkg in pkgs_installed if pkg != PKG_NAME]
    elif PKG_NAME in pkgs:
        print(Fore.YELLOW + 'Use pip to update the ' + PKG_NAME)
        del pkgs[pkgs.index(PKG_NAME)]

    w = [0, 0]
    pkgs_to_update = {}
    for pkg in pkgs:

        err_msg = Style.BRIGHT + Fore.RED + 'Cannot update {}: '.format(pkg)

        if pkg not in pkgs_installed:
            print(err_msg + 'package not installed')
            continue

        if pkg not in pkgs_github:
            print(err_msg + 'package not found on github')
            continue

        installed_version = pkgs_installed[pkg]['version']

        if tag is not None:
            if tag in pkgs_github[pkg]['tags']:
                pkgs_to_update[pkg] = (installed_version, '[tag:{}]'.format(tag))
            else:
                print(err_msg + 'a "{}" tag does not exist'.format(tag))
                continue
        elif branch is not None:
            if branch in pkgs_github[pkg]['branches']:
                pkgs_to_update[pkg] = (installed_version, '[branch:{}]'.format(branch))
            else:
                print(err_msg + 'a "{}" branch does not exist'.format(branch))
                continue
        else:
            github_version = pkgs_github[pkg]['version']
            if not github_version:
                print(err_msg + 'the github repository does not contain a release')
                continue
            elif parse_version(github_version) > parse_version(installed_version):
                pkgs_to_update[pkg] = (installed_version, github_version)
            else:
                print(Fore.YELLOW + 'The {} package is already the latest [{}]'.format(pkg, installed_version))
                continue

        w = [max(w[0], len(pkg)), max(w[1], len(installed_version))]

    if pkgs_to_update:
        pkgs_to_update = _sort_packages(pkgs_to_update)

        msg = '\nThe following MSL packages will be {0}UPDATED{1}:\n'.format(Fore.CYAN, Fore.RESET)
        for pkg in pkgs_to_update:
            local, remote = pkgs_to_update[pkg]
            pkg += ': '
            msg += '\n  ' + pkg.ljust(w[0]+2) + local.ljust(w[1]) + ' --> ' + remote

        print(msg)
        if not (yes or _ask_proceed()):
            return
        print('')

        exe = [sys.executable, '-m', 'pip', 'install']
        options = ['--upgrade', '--force-reinstall', '--no-deps']
        for pkg in pkgs_to_update:
            repo = ['https://github.com/MSLNZ/{}/archive/{}.zip'.format(pkg, zip_name)]
            subprocess.call(exe + options + repo)
    else:
        print('No MSL packages to update')
