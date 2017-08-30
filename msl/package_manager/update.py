"""
Use pip to update MSL packages.
"""
import sys
import subprocess
from distutils.version import StrictVersion

from colorama import Fore, Style

from . import PKG_NAME
from .helper import github, installed, _get_names, _ask_proceed, _sort_packages


def update(names='ALL', yes=False, update_github_cache=False):
    """Use pip to update MSL packages.

    Parameters
    ----------
    names : :obj:`str` or :obj:`list` of :obj:`str`, optional
        The name of a single MSL package or a list of MSL package names to update. 
        Default is to update all MSL packages (except for the **msl-package-manager**).
    yes : :obj:`bool`, optional
        Don't ask for confirmation to update. Default is to ask before updating.
    update_github_cache : :obj:`bool`, optional
        The information about the repositories that are available on GitHub_ are
        temporarily cached to use for subsequent calls to this function. After
        24 hours the cache is automatically updated. Set `update_github_cache`
        to be :obj:`True` to force the cache to be updated when you call this
        function.
    """
    pkgs_github = github(update_github_cache)
    if not pkgs_github:
        return
    pkgs_installed = installed()

    _names = _get_names(names)

    if _names:
        pkgs = [p for p in _names if p in pkgs_installed]
    else:
        pkgs = [pkg for pkg in pkgs_installed if pkg != PKG_NAME]

    w = [0, 0, 0]
    pkgs_to_update = {}
    for pkg in pkgs:

        try:
            github_version = pkgs_github[pkg][0]
        except KeyError:
            print(Style.BRIGHT + Fore.RED + 'Cannot update {0} -- package not found on github'.format(pkg))
            continue

        if not github_version:
            print(Style.BRIGHT + Fore.RED + 'Cannot update {0} -- github repository does not contain a release tag'.format(pkg))
            continue

        try:
            installed_version = pkgs_installed[pkg][0]
        except KeyError:
            pkgs_to_update[pkg] = (github_version, '')
            continue

        if StrictVersion(github_version) > StrictVersion(installed_version):
            pkgs_to_update[pkg] = (github_version, installed_version)
            w = [max(w[0], len(pkg)), max(w[1], len(installed_version)), max(w[2], len(github_version))]
        else:
            print(Fore.YELLOW + 'The {0} package is already the latest'.format(pkg))

    if pkgs_to_update:
        pkgs_to_update = _sort_packages(pkgs_to_update)

        msg = '\nThe following MSL packages will be {0}UPDATED{1}:\n'.format(Fore.CYAN, Fore.RESET)
        for pkg in pkgs_to_update:
            have = pkgs_to_update[pkg][1]
            want = pkgs_to_update[pkg][0]
            msg += '\n  ' + pkg.ljust(w[0]) + ': ' + have.ljust(w[1]) + ' --> ' + want.ljust(w[2])

        print(msg)
        if not (yes or _ask_proceed()):
            return
        print('')

        for pkg in pkgs_to_update:
            repo = 'https://github.com/MSLNZ/{0}/archive/master.zip'.format(pkg)
            subprocess.call([sys.executable, '-m', 'pip', 'install', repo, '--upgrade', '--process-dependency-links'])
    else:
        print(Fore.CYAN + 'No MSL packages to update')
