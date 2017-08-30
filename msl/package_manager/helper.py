"""
Helper functions for the MSL Package Manager.
"""
import pip
import json
import getpass
import logging
import subprocess
from collections import OrderedDict

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
    except FileNotFoundError:
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
    except FileNotFoundError:
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


def github(get_release_version=False):
    """Get the list of MSL repositories that are available on GitHub.

    Parameters
    ----------
    get_release_version : :obj:`bool`, optional
        Get the latest release version information. Getting the release version 
        will make this function take longer to finish. Also, the repository might
        not have published a release tag so the release information might not be 
        available. Default is :obj:`False`.

    Returns
    -------
    :obj:`dict` 
        With the repository name for the keys and the values are a :obj:`list`
        of [version, description].
    """
    try:
        repos = json.loads(urlopen('https://api.github.com/orgs/MSLNZ/repos').read().decode())
    except:
        # it is possible to get an "API rate limit exceeded for" error if you call this
        # function too often or maybe the user does not have an internet connection
        logging.log(logging.ERROR, 'Cannot connect to GitHub')
        return {}

    pkgs = {}
    for repo in repos:
        if repo['name'].startswith('msl-'):
            version = ''
            if get_release_version:
                url = 'https://api.github.com/repos/MSLNZ/{}/releases/latest'.format(repo['name'])
                try:
                    version = json.loads(urlopen(url).read().decode())['name'].replace('v', '')
                except:
                    pass
            pkgs[repo['name']] = [version, repo['description']]
    return pkgs


def installed():
    """Get the MSL packages that are installed.

    Returns
    -------
    :obj:`dict` 
        With the repository name for the keys and the values are a :obj:`list`
        of [version, description].
    """
    pkgs = {}
    for pkg in pip.get_installed_distributions():
        if pkg.key.startswith('msl-'):
            description = 'unknown'
            for item in pkg._get_metadata(pkg.PKG_INFO):
                if 'Summary:' in item:
                    description = item.split('Summary:')[1].strip()
                    break
            pkgs[pkg.key] = [pkg.version, description]
    return pkgs


def _get_packages(_command, _names, _yes, get_release_version=False):
    """
    Returns a sorted dictionary of the available MSL packages, from either pip or GitHub.
    """
    pkgs = {}
    pkgs_installed = installed()
    names = _get_names(_names)

    if _command == 'install':

        pkgs_github = github(get_release_version)
        if len(names) == 0:
            names = [pkg for pkg in pkgs_github if pkg != PKG_NAME]

        for name in names:
            if name in pkgs_installed:
                print(Style.BRIGHT + Fore.YELLOW + 'The {0} package is already installed'.format(name))
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
        pkgs = OrderedDict([(k, pkgs[k]) for k in sorted(pkgs)])

        w = 0
        show_version = False
        for p in pkgs:
            w = max(w, len(p))
            if not show_version:
                show_version = len(pkgs[p][0]) > 0

        msg = 'The following MSL packages will be {0}ED:\n'.format(_command.upper())
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
        print('No MSL packages to ' + _command)

    return pkgs


def _get_names(names):
    """Convert `names` to friendly list of names."""

    if isinstance(names, str):
        check_names = [] if names == 'ALL' else [names]
    elif isinstance(names, (list, tuple)) and isinstance(names[0], str):
        check_names = names[:]
    else:
        raise TypeError('The package names must be either a string or a list of strings')

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
