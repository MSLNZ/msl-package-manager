"""
Helper functions for the MSL Package Manager.
"""
import os
import sys
import pip
import json
import time
import getpass
import tempfile
import subprocess
from collections import OrderedDict
from multiprocessing.pool import ThreadPool

from colorama import Fore, Style

from msl.package_manager import IS_PYTHON2, IS_PYTHON3, PKG_NAME

if IS_PYTHON2:
    from urllib2 import urlopen
elif IS_PYTHON3:
    from urllib.request import urlopen
else:
    raise NotImplementedError('Python major version is not 2 or 3')


__all__ = ['get_username', 'get_email', 'get_input', 'github', 'installed']


def get_username():
    """Automatically determine the name of the user.

    If git_ is installed then it returns the ``user.name`` parameter from the user's git_
    account. If git_ is not installed then use :func:`getpass.getuser` to determine
    the username from an environment variable.

    .. _git: https://git-scm.com

    Returns
    -------
    :obj:`str`
        The user's name.
    """
    try:
        p1 = subprocess.Popen(['git', 'config', 'user.name'], stdout=subprocess.PIPE)
        return p1.communicate()[0].decode().strip()
    except IOError:
        return getpass.getuser()


def get_email():
    """Try to determine the user's email address.

    If git_ is installed then it returns the ``user.email`` parameter from the user's git_
    account to use as the user's email address. If git_ is not installed then returns
    :obj:`None`.

    .. _git: https://git-scm.com

    Returns
    -------
    :obj:`str` or :obj:`None`
        The user's email address.
    """
    try:
        p2 = subprocess.Popen(['git', 'config', 'user.email'], stdout=subprocess.PIPE)
        return p2.communicate()[0].decode().strip()
    except IOError:
        return None


def get_input(msg):
    """Get the user input (for Python 2 and 3).

    Parameters
    ----------
    msg : :obj:`str`
        The message to display.

    Returns
    -------
    :obj:`str`
        The user's input from :obj:`sys.stdin`.

    Raises
    ------
    NotImplementedError
        If the Python major version is not 2 or 3.
    """
    if IS_PYTHON2:
        return raw_input(msg)
    elif IS_PYTHON3:
        return input(msg)
    else:
        raise NotImplementedError('Python major version is not 2 or 3')


def github(force=False):
    """Get the list of MSL repositories that are available on GitHub_.

    .. _GitHub: https://github.com/MSLNZ

    Parameters
    ----------
    force : :obj:`bool`, optional
        The information about the repositories that are available on GitHub_ are
        temporarily cached to use for subsequent calls to this function. After
        24 hours the cache is automatically updated. Set `force` to be :obj:`True`
        to force the cache to be updated when you call this function.

    Returns
    -------
    :obj:`dict` of :obj:`tuple`
        With the repository name for the keys and the values are (version, description).
    """
    def fetch_version(repo_info):
        repo_name, description = repo_info
        url = 'https://api.github.com/repos/MSLNZ/{}/releases/latest'.format(repo_name)
        try:
            return repo_name, json.loads(urlopen(url).read().decode('utf-8'))['name'].replace('v', ''), description
        except:
            return repo_name, '', description

    path = os.path.join(tempfile.gettempdir(), 'msl-github-repo-cache.json')

    cached_msg = Fore.CYAN + 'Loaded the cached information about the GitHub repositories'

    cached_pgks = None
    if os.path.isfile(path):
        with open(path, 'r') as f:
            cached_pgks = _sort_packages(json.load(f))

    one_day = 60 * 60 * 24
    if (not force) and (cached_pgks is not None) and (time.time() < os.path.getmtime(path) + one_day):
        print(cached_msg)
        return cached_pgks

    try:
        print(Fore.CYAN + 'Inspecting repositories on GitHub')
        repos = json.loads(urlopen('https://api.github.com/orgs/MSLNZ/repos').read().decode('utf-8'))
    except Exception as err:
        # it is possible to get an "API rate limit exceeded for" error if you call this
        # function too often or maybe the user does not have an internet connection
        print(Style.BRIGHT + Fore.RED + 'Cannot connect to GitHub -- {}'.format(err))
        if cached_pgks is not None:
            print(cached_msg)
            return cached_pgks
        print('Perhaps the GitHub API rate limit was exceeded. Please wait a while and try again later...')
        return {}

    pkgs = {}
    info = [(repo['name'], repo['description']) for repo in repos if repo['name'].startswith('msl-')]
    results = ThreadPool(len(info)).imap_unordered(fetch_version, info)
    for name, version, description in results:
        pkgs[name] = (version, description)

    with open(path, 'w') as fp:
        json.dump(pkgs, fp)

    return _sort_packages(pkgs)


def installed():
    """Get the MSL packages that are installed.

    Returns
    -------
    :obj:`dict` of :obj:`tuple`
        With the package name for the keys and the values are (version, description).
    """
    print(Fore.CYAN + 'Inspecting packages in {0}'.format(os.path.dirname(sys.executable)))
    pkgs = {}
    for pkg in pip.get_installed_distributions():
        if pkg.key.startswith('msl-'):
            description = 'unknown'
            for item in pkg._get_metadata(pkg.PKG_INFO):
                if 'Summary:' in item:
                    description = item.split('Summary:')[1].strip()
                    break
            pkgs[pkg.key] = [pkg.version, description]
    return _sort_packages(pkgs)


def _get_packages(_command, _names, _yes, update_github_cache=False):
    """
    Returns a sorted dictionary of the available MSL packages, from either pip or GitHub.
    """
    pkgs = {}
    pkgs_installed = installed()
    names = _get_names(_names)

    if _command == 'install':

        pkgs_github = github(update_github_cache)
        if len(names) == 0:
            names = [pkg for pkg in pkgs_github if pkg != PKG_NAME]

        for name in names:
            if name in pkgs_installed:
                print(Fore.YELLOW + 'The {0} package is already installed'.format(name))
            elif name not in pkgs_github:
                print(Style.BRIGHT + Fore.RED + 'Cannot install {0} -- package not found'.format(name))
            else:
                pkgs[name] = pkgs_github[name]

    elif _command == 'uninstall':
        if len(names) == 0:
            names = [pkg for pkg in pkgs_installed if pkg != PKG_NAME]

        for name in names:
            if name == PKG_NAME:
                print(Style.BRIGHT + Fore.RED + 'Cannot uninstall {0} using itself. Use "pip uninstall {0}"'.format(PKG_NAME))
            elif name not in pkgs_installed:
                print(Style.BRIGHT + Fore.RED + 'Cannot uninstall {0} -- package not found'.format(name))
            else:
                pkgs[name] = pkgs_installed[name]

    if pkgs:
        pkgs = _sort_packages(pkgs)

        w = 0
        show_version = False
        for p in pkgs:
            w = max(w, len(p))
            if not show_version:
                show_version = len(pkgs[p][0]) > 0

        msg = '\nThe following MSL packages will be {0}{1}ED{2}:\n'.format(Fore.CYAN, _command.upper(), Fore.RESET)
        for pkg, values in pkgs.items():
            pkg_name = pkg + ':' if show_version else pkg
            msg += '\n  ' + pkg_name.ljust(w+1)
            if show_version:
                msg += ' ' + values[0]

        print(msg)
        if not (_yes or _ask_proceed()):
            return {}
        print('')
    else:
        print(Fore.CYAN + 'No MSL packages to ' + _command)

    return pkgs


def _get_names(names):
    """Convert `names` to friendly list of names."""

    if isinstance(names, str):
        check_names = [] if names == 'ALL' else [names]
    elif isinstance(names, (list, tuple)) and isinstance(names[0], str):
        check_names = names[:]
    else:
        assert False, 'The package names must be either a string or a list of strings'

    _names = []
    for name in check_names:
        if name.startswith('msl-'):
            _names.append(name)
        else:
            _names.append('msl-' + name)

    return _names


def _ask_proceed():
    """Ask whether to proceed with the command, e.g. install, uninstall, update"""
    ask = '\nProceed (y/[n])? '
    res = get_input(ask).lower()
    while True:
        if res == 'y':
            return True
        elif res == 'n' or len(res) == 0:
            return False
        else:
            res = get_input(ask).lower()


def _sort_packages(pkgs):
    """Sort the MSL packages by name"""
    return OrderedDict([(k, pkgs[k]) for k in sorted(pkgs)])
