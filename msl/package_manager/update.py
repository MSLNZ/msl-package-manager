"""
Update MSL packages.
"""
import sys
import subprocess
from pkg_resources import parse_version

from colorama import Fore

from . import PKG_NAME, helper


def update(names=None, yes=False, update_github_cache=False, branch=None, tag=None):
    """Update MSL packages.

    .. _repositories: https://github.com/MSLNZ

    Parameters
    ----------
    names : :obj:`str` or :obj:`list` of :obj:`str`, optional
        The name(s) of MSL package(s) to update. The default is to update
        **all** MSL packages (except for the **MSL Package Manager**).
    yes : :obj:`bool`, optional
        If :obj:`True` then don't ask for confirmation before updating.
        The default is to ask before updating.
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

        .. attention::
           Cannot specify both a `branch` and a `tag`.

        .. note::
           If you specify a `branch` or a `tag` then the update will be forced.
    """
    zip_name = helper.get_zip_name(branch, tag)
    if zip_name is None:
        return

    pkgs_github = helper.github(update_github_cache)
    if not pkgs_github:
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

        if name not in pkgs_github:
            helper.print_error(err_msg + 'package not found on github')
            continue

        installed_version = pkgs_installed[name]['version']

        if tag is not None:
            if tag in pkgs_github[name]['tags']:
                pkgs_to_update[name] = (installed_version, '[tag:{}]'.format(tag))
            else:
                helper.print_error(err_msg + 'a "{}" tag does not exist'.format(tag))
                continue
        elif branch is not None:
            if branch in pkgs_github[name]['branches']:
                pkgs_to_update[name] = (installed_version, '[branch:{}]'.format(branch))
            else:
                helper.print_error(err_msg + 'a "{}" branch does not exist'.format(branch))
                continue
        else:
            github_version = pkgs_github[name]['version']
            if not github_version:
                helper.print_error(err_msg + 'the github repository does not contain a release')
                continue
            elif parse_version(github_version) > parse_version(installed_version):
                pkgs_to_update[name] = (installed_version, github_version)
            else:
                helper.print_warning('The {} package is already the latest [{}]'.format(name, installed_version))
                continue

        w = [max(w[0], len(name)), max(w[1], len(installed_version))]

    if pkgs_to_update:
        pkgs_to_update = helper.sort_packages(pkgs_to_update)

        msg = '\nThe following MSL packages will be {}UPDATED{}:\n'.format(Fore.CYAN, Fore.RESET)
        for pkg in pkgs_to_update:
            local, remote = pkgs_to_update[pkg]
            pkg += ': '
            msg += '\n  ' + pkg.ljust(w[0]+2) + local.ljust(w[1]) + ' --> ' + remote

        print(msg)
        if not (yes or helper.ask_proceed()):
            return
        print('')

        exe = [sys.executable, '-m', 'pip', 'install']
        options = ['--upgrade', '--force-reinstall', '--no-deps']
        for pkg in pkgs_to_update:
            repo = ['https://github.com/MSLNZ/{}/archive/{}.zip'.format(pkg, zip_name)]
            subprocess.call(exe + options + repo)
    else:
        print('No MSL packages to update')
