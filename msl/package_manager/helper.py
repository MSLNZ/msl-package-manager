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


def ask_proceed():
    """Ask whether to proceed with the command.

    Returns
    -------
    :obj:`True`
        Whether to proceed.
    """
    ask = '\nProceed (y/[n])? '
    response = get_input(ask).lower()
    while True:
        if response.startswith('y'):
            return True
        elif response.startswith('n') or not response:
            return False
        else:
            print('Invalid response')
            response = get_input(ask).lower()


def check_msl_prefix(names):
    """Ensures that the package names start with ``msl-``.

     Parameters
     ----------
     names : :obj:`str` or :obj:`list` of :obj:`str`
        The package names.

     Returns
     -------
     :obj:`list` of :obj:`str`
        A list of package names with the ``msl-`` prefix.
    """
    if names is None:
        return []
    elif not isinstance(names, (list, tuple)):
        check_names = [names]
    else:
        check_names = names

    _names = []
    for name in check_names:
        if name.startswith('msl-'):
            _names.append(name)
        else:
            _names.append('msl-' + name)
    return _names


def create_install_list(names, branch, tag, update_github_cache):
    """Create a list of package names to ``install``.

    .. _repository: https://github.com/MSLNZ

    Parameters
    ----------
    names : :obj:`str` or :obj:`list` of :obj:`str`
        The name of a single GitHub repository_ or a list of repository_ names.
    branch : :obj:`str`
        The name of a GitHub branch to use for the ``install``.
    tag : :obj:`str`
        The name of a GitHub tag to use for the ``install``.
    update_github_cache : :obj:`bool`
        Whether to force the GitHub cache to be updated when you call this function.

    Returns
    -------
    :obj:`dict` of :obj:`dict`
        The MSL packages to ``install``.
    """
    zip_name = get_zip_name(branch, tag)
    if zip_name is None:
        return

    pkgs_installed = installed()
    pkgs_github = github(update_github_cache)

    names = check_msl_prefix(names)
    if not names:
        names = [pkg for pkg in pkgs_github if pkg != PKG_NAME]

    pkgs = {}
    for name in names:
        if name in pkgs_installed:
            print_warning('The {} package is already installed'.format(name))
        elif name not in pkgs_github:
            print_error('Cannot install {}: package not found'.format(name))
        elif branch is not None and branch not in pkgs_github[name]['branches']:
            print_error('Cannot install {}: a "{}" branch does not exist'.format(name, branch))
        elif tag is not None and tag not in pkgs_github[name]['tags']:
            print_error('Cannot install {}: a "{}" tag does not exist'.format(name, tag))
        else:
            pkgs[name] = pkgs_github[name]
    return pkgs


def create_uninstall_list(names):
    """Create a list of package names to ``uninstall``.

    Parameters
    ----------
    names : :obj:`str` or :obj:`list` of :obj:`str`
        The name(s) of the package(s) to ``uninstall``.

    Returns
    -------
    :obj:`dict` of :obj:`dict`
        The MSL packages to ``uninstall``.
    """

    pkgs_installed = installed()

    names = check_msl_prefix(names)
    if not names:
        names = [pkg for pkg in pkgs_installed if pkg != PKG_NAME]

    pkgs = {}
    for name in names:
        if name == PKG_NAME:
            print_error('The MSL Package Manager cannot uninstall itself. Use "pip uninstall {}"'.format(PKG_NAME))
        elif name not in pkgs_installed:
            print_error('Cannot uninstall {}: package not installed'.format(name))
        else:
            pkgs[name] = pkgs_installed[name]
    return pkgs


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
        return p2.communicate()[0].decode('utf-8').strip()
    except IOError:
        return None


def get_input(msg):
    """Get the input from the user (for Python 2 and 3).

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
        return p1.communicate()[0].decode('utf-8').strip()
    except IOError:
        return getpass.getuser()


def get_zip_name(branch, tag):
    """Returns the name of a zip file in the MSLNZ-GitHub archive.

    Parameters
    ----------
    branch : :obj:`str` or :obj:`None`
        The name of a GitHub branch.
    tag : :obj:`str` or :obj:`None`
        The name of a GitHub tag.

    Returns
    -------
    :obj:`str`
        The name of the zip file or :obj:`None` if both `branch`
        and `tag` were specified.
    """
    if branch is not None and tag is not None:
        print_error('Cannot specify both a branch ({}) and a tag ({})'.format(branch, tag))
        return None
    elif branch is None and tag is None:
        return 'master'
    elif branch is not None:
        return branch
    elif tag is not None:
        return tag
    else:
        assert False, 'This branch ({}) and tag ({}) combo has not been handled'.format(branch, tag)


def github(update_github_cache=False):
    """Get the list of MSL repositories_ that are available on GitHub.

    .. _repositories: https://github.com/MSLNZ

    Parameters
    ----------
    update_github_cache : :obj:`bool`, optional
        The information about the repositories_ that are available on GitHub are
        cached to use for subsequent calls to this function. After 24 hours the
        cache is automatically updated. Set `update_github_cache` to be :obj:`True`
        to force the cache to be updated when you call this function.

    Returns
    -------
    :obj:`dict` of :obj:`dict`
        The MSL repositories_ that are available on GitHub.
    """
    def fetch(url_suffix):
        url = 'https://api.github.com/repos/MSLNZ/' + url_suffix
        return json.loads(urlopen(url).read().decode('utf-8'))

    def fetch_latest_release(name):
        try:
            return name, fetch(name+'/releases/latest')['name'].replace(u'v', u'')
        except:
            return name, ''

    def fetch_tags(name):
        try:
            return name, [tag['name'] for tag in fetch(name+'/tags')]
        except:
            return name, []

    def fetch_branches(name):
        try:
            return name, [branch['name'] for branch in fetch(name+'/branches')]
        except:
            return name, []

    path = os.path.join(tempfile.gettempdir(), 'msl-github-repo-cache.json')

    cached_msg = 'Loaded the cached information about the GitHub repositories'

    cached_pgks = None
    if os.path.isfile(path):
        with open(path, 'r') as f:
            cached_pgks = sort_packages(json.load(f))

    one_day = 60 * 60 * 24
    if (not update_github_cache) and (cached_pgks is not None) and (time.time() < os.path.getmtime(path) + one_day):
        print_info(cached_msg)
        return cached_pgks

    try:
        print_info('Inspecting repositories on GitHub')
        repos = json.loads(urlopen('https://api.github.com/orgs/MSLNZ/repos').read().decode('utf-8'))
    except Exception as err:
        # it is possible to get an "API rate limit exceeded for" error if you call this
        # function too often or maybe the user does not have an internet connection
        print_error('Cannot connect to GitHub -- {}'.format(err))
        if cached_pgks is not None:
            print_info(cached_msg)
            return cached_pgks
        print('Perhaps the GitHub API rate limit was exceeded. Please wait a while and try again later...')
        return {}

    pkgs = {}
    for repo in repos:
        if repo['name'].startswith('msl-'):
            pkgs[repo['name']] = {}
            pkgs[repo['name']]['description'] = repo['description']

    latest_thread = ThreadPool(len(pkgs)).imap_unordered(fetch_latest_release, pkgs)
    tags_thread = ThreadPool(len(pkgs)).imap_unordered(fetch_tags, pkgs)
    branches_thread = ThreadPool(len(pkgs)).imap_unordered(fetch_branches, pkgs)
    for repo_name, value in latest_thread:
        pkgs[repo_name]['version'] = value
    for repo_name, value in tags_thread:
        pkgs[repo_name]['tags'] = value
    for repo_name, value in branches_thread:
        pkgs[repo_name]['branches'] = value

    with open(path, 'w') as fp:
        json.dump(pkgs, fp)

    return sort_packages(pkgs)


def installed():
    """Get the MSL packages that are installed.

    Returns
    -------
    :obj:`dict` of :obj:`dict`
        The MSL packages that are installed.
    """
    print_info('Inspecting packages in {}'.format(os.path.dirname(sys.executable)))
    pkgs = {}
    for pkg in pip.get_installed_distributions():
        if pkg.key.startswith('msl-'):
            description = 'unknown'
            for item in pkg._get_metadata(pkg.PKG_INFO):
                if 'Summary:' in item:
                    description = item.split('Summary:')[1].strip()
                    break
            pkgs[pkg.key] = {}
            pkgs[pkg.key]['version'] = pkg.version
            pkgs[pkg.key]['description'] = description
    return sort_packages(pkgs)


def print_error(msg):
    """Print an error message.

    Parameters
    ----------
    msg : :obj:`str`
        The message to print.
    """
    print(Style.BRIGHT + Fore.RED + msg)


def print_info(msg):
    """Print an info message.

    Parameters
    ----------
    msg : :obj:`str`
        The message to print.
    """
    print(Fore.CYAN + msg)


def print_warning(msg):
    """Print a warning message.

    Parameters
    ----------
    msg : :obj:`str`
        The message to print.
    """
    print(Fore.YELLOW + msg)


def print_install_uninstall_message(packages, action, branch=None, tag=None):
    """Print the ``install`` or ``uninstall`` summary for what is going to happen.

    Parameters
    ----------
    packages : :obj:`dict`
        The packages that are affected.
    action : :obj:`str`
        The text to show in color and in upper case about what's happening.
    branch : :obj:`str`, optional
        The name of a GitHub branch to use for the ``install``.
        *Only used when installing packages*.
    tag : :obj:`str`, optional
        The name of a GitHub tag to use for the ``install``.
        *Only used when installing packages*.
    """
    pkgs = sort_packages(packages)

    w = 0
    has_version_info = False
    for p in pkgs:
        w = max(w, len(p))
        if not has_version_info:
            has_version_info = len(pkgs[p]['version']) > 0

    msg = '\nThe following MSL packages will be {}{}{}:\n'.format(Fore.CYAN, action, Fore.RESET)
    for pkg, values in pkgs.items():
        if has_version_info or branch or tag:
            pkg += ':'
        msg += '\n  ' + pkg.ljust(w + 1)
        if branch is not None:
            msg += ' [branch:{}]'.format(branch)
        elif tag is not None:
            msg += ' [tag:{}]'.format(tag)
        elif has_version_info:
            msg += ' ' + values['version']

    print(msg)


def sort_packages(pkgs):
    """Sort the MSL packages by the name of the package.

    Parameters
    ----------
    pkgs : :obj:`dict`
        The MSL packages.

    Returns
    -------
    :obj:`collections.OrderedDict`
        The packages sorted by name.
    """
    return OrderedDict([(k, pkgs[k]) for k in sorted(pkgs)])
