"""
Functions for the API.

.. _packages: https://pypi.org/search/?q=msl-
.. _PyPI: https://pypi.org/search/?q=msl-
.. _git: https://git-scm.com
.. _repositories: https://github.com/MSLNZ
.. _repository: https://github.com/MSLNZ
.. _GitHub: https://github.com/MSLNZ

"""
import re
import os
import sys
import json
import time
import getpass
import tempfile
import importlib
import subprocess
import pkg_resources
from datetime import datetime
from collections import OrderedDict
from multiprocessing.pool import ThreadPool

from colorama import Fore, Style

from . import IS_PYTHON2
from . import IS_PYTHON3
from . import PKG_NAME

if IS_PYTHON2:
    from urllib2 import urlopen
elif IS_PYTHON3:
    from urllib.request import urlopen
else:
    raise NotImplementedError('Python major version is not 2 or 3')


def get_email():
    """Try to determine the user's email address.

    If git_ is installed then it returns the ``user.email`` parameter from the user's git_
    account to use as the user's email address. If git_ is not installed then returns
    :obj:`None`.

    Returns
    -------
    :class:`str` or :obj:`None`
        The user's email address.
    """
    try:
        p2 = subprocess.Popen(['git', 'config', 'user.email'], stdout=subprocess.PIPE)
        return p2.communicate()[0].decode('utf-8').strip()
    except IOError:
        return None


def get_username():
    """Automatically determine the name of the user.

    If git_ is installed then it returns the ``user.name`` parameter from the user's git_
    account. If git_ is not installed then use :func:`getpass.getuser` to determine
    the username from an environment variable.

    Returns
    -------
    :class:`str`
        The user's name.
    """
    try:
        p1 = subprocess.Popen(['git', 'config', 'user.name'], stdout=subprocess.PIPE)
        return p1.communicate()[0].decode('utf-8').strip()
    except IOError:
        return getpass.getuser()


def github(update_cache=False, quiet=False):
    """Get the MSL repositories that are available on GitHub_.

    Parameters
    ----------
    update_cache : :class:`bool`, optional
        The information about the repositories_ that are available on GitHub are
        cached to use for subsequent calls to this function. After 24 hours the
        cache is automatically updated. Set `update_cache` to be :obj:`True`
        to force the cache to be updated when you call this function.
    quiet : :class:`bool`, optional
        Whether to suppress the :func:`print` statements.

    Returns
    -------
    :class:`dict` of :class:`dict`
        The MSL repositories_ that are available on GitHub.
    """
    def fetch(url_suffix):
        url = 'https://api.github.com/repos/MSLNZ/' + url_suffix
        return json.loads(urlopen(url).read().decode('utf-8'))

    def fetch_latest_release(name):
        try:
            ret = fetch(name + '/releases/latest')
            latest = ret['name'] if ret['name'] else ret['tag_name']
            return name, latest.replace(u'v', u'')
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

    cached_pgks, path, cached_msg = _inspect_github_pypi('github', update_cache, quiet=quiet)
    if cached_pgks:
        return cached_pgks

    try:
        if not quiet:
            _print_info('Inspecting repositories on GitHub')
        repos = json.loads(urlopen('https://api.github.com/orgs/MSLNZ/repos').read().decode('utf-8'))
    except Exception as err:
        # it is possible to get an "API rate limit exceeded for" error if you call this
        # function too often or maybe the user does not have an internet connection
        if not quiet:
            try:
                r = json.loads(urlopen('https://api.github.com/rate_limit').read().decode('utf-8'))
                if r['rate']['remaining'] == 0:
                    hms = datetime.fromtimestamp(int(r['rate']['reset'])).strftime('%H:%M:%S')
                    msg = 'The GitHub API rate limit was exceeded. Retry at {}'.format(hms)
                else:
                    msg = 'Unknown error... there are still {} of {} GitHub requests remaining'.format(
                        r['rate']['remaining'], r['rate']['limit'])
            except:
                msg = 'Perhaps the computer does not have internet access'
            _print_error('Cannot connect to GitHub -- {}\n{}'.format(err, msg))

        cached_pgks, path, cached_msg = _inspect_github_pypi('github', False, quiet=quiet)
        if cached_pgks:
            return cached_pgks

        return dict()

    pkgs = dict()
    for repo in repos:
        if repo['name'].startswith('msl-'):
            pkgs[repo['name']] = dict()
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

    return _sort_packages(pkgs)


def installed(quiet=False):
    """Get the MSL packages that are installed.

    Parameters
    ----------
    quiet : :class:`bool`, optional
        Whether to suppress the :func:`print` statements.

    Returns
    -------
    :class:`dict` of :class:`dict`
        The MSL packages that are installed.
    """
    if not quiet:
        _print_info('Inspecting packages in {}'.format(os.path.dirname(sys.executable)))

    # refresh the working_set
    importlib.reload(pkg_resources)

    pkgs = {}
    for dist in pkg_resources.working_set:
        if not dist.key.startswith('msl-'):
            continue

        description = ''
        if dist.has_metadata(dist.PKG_INFO):
            for line in dist.get_metadata_lines(dist.PKG_INFO):
                if line.startswith('Summary:'):
                    description = line[8:].strip()
                    break

        pkgs[dist.project_name] = dict()
        pkgs[dist.project_name]['version'] = dist.version
        pkgs[dist.project_name]['description'] = description

    return _sort_packages(pkgs)


def print_packages(from_github=False, detailed=False, from_pypi=False, update_cache=False):
    """Print the MSL packages that are available.

    The list of packages can be either those that are installed, are
    available as repositories_ on GitHub or are available as packages_ on PyPI.

    Parameters
    ----------
    from_github : :class:`bool`, optional
        Whether to show the MSL packages that are available as GitHub repositories_.
        The default action is to show the MSL packages that are installed.
    detailed : :class:`bool`, optional
        Whether to show detailed information about the MSL packages that are available
        as GitHub repositories_ (i.e., displays additional information about the
        branches and tags). Only used if `from_github` is :obj:`True`.
    from_pypi : :class:`bool`, optional
        Whether to show the MSL packages_ that are available on PyPI. The default
        action is to show the MSL packages that are installed.
    update_cache : :class:`bool`, optional
        The information about the MSL packages_ that are available on PyPI and about
        the repositories_ that are available on GitHub are cached to use for subsequent
        calls to this function. After 24 hours the cache is automatically updated. Set
        `update_cache` to be :obj:`True` to force the cache to be updated when you call
        this function.
    """
    if from_github:
        typ, pkgs = 'Repository', github(update_cache)
        if not pkgs:
            return
    elif from_pypi:
        typ, pkgs = 'PyPI Package', pypi(update_cache)
        if not pkgs:
            return
    else:
        typ, pkgs = 'Package', installed()

    if detailed and from_github:
        print('')
        indent = '    '
        for p in pkgs:
            print(p + ':')
            for key in sorted(pkgs[p]):
                value = pkgs[p][key]
                print(indent + key + ':')
                if not value:
                    continue
                if not isinstance(value, list):
                    value = [value]
                print(indent + indent + ('\n' + indent + indent).join(v for v in value))
        return

    # determine the maximum width of each column
    header = ['MSL ' + typ, 'Version', 'Description']
    w = [len(h) for h in header]
    for p in pkgs:
        w = [
            max(w[0], len(p)),
            max(w[1], len(pkgs[p]['version'])),
            max(w[2], len(pkgs[p]['description']) if pkgs[p]['description'] else 0)
        ]

    # print the results
    print('')
    print(' '.join(header[i].ljust(w[i]) for i in range(len(header))))
    print(' '.join('-' * w for w in w))
    for p in sorted(pkgs):
        description = pkgs[p]['description'] if pkgs[p]['description'] else ''
        print(p.ljust(w[0]) + ' ' + pkgs[p]['version'].ljust(w[1]) + ' ' + description.ljust(w[2]))


def pypi(update_cache=False, quiet=False):
    """Get the MSL packages that are available on PyPI_.

    Parameters
    ----------
    update_cache : :class:`bool`, optional
        The information about the MSL packages_ that are available on PyPI are
        cached to use for subsequent calls to this function. After 24 hours the
        cache is automatically updated. Set `update_cache` to be :obj:`True`
        to force the cache to be updated when you call this function.
    quiet : :class:`bool`, optional
        Whether to suppress the :func:`print` statements.

    Returns
    -------
    :class:`dict` of :class:`dict`
        The MSL packages_ that are available on PyPI.
    """
    cached_pgks, path, cached_msg = _inspect_github_pypi('pypi', update_cache, quiet=quiet)
    if cached_pgks:
        return cached_pgks

    try:
        if not quiet:
            _print_info('Inspecting packages on PyPI')
        p2 = subprocess.Popen([sys.executable, '-m', 'pip', 'search', 'msl-'], stdout=subprocess.PIPE)
        stdout = p2.communicate()[0].decode('utf-8').strip()
    except Exception as err:
        if not quiet:
            _print_error('Cannot connect to PyPI -- {}'.format(err))
        if cached_pgks is not None:
            if not quiet:
                _print_info(cached_msg)
            return cached_pgks
        return dict()

    pkgs = dict()
    for line in stdout.splitlines():
        match = re.match(r'(.*)\s+\((.*)\)\s+-\s+(.*)', line)
        if match and match.group(1).lower().startswith('msl-'):
            pkgs[match.group(1)] = {
                'version': match.group(2),
                'description': match.group(3),
            }

    with open(path, 'w') as fp:
        json.dump(pkgs, fp)

    return _sort_packages(pkgs)


def _ask_proceed():
    """Ask whether to proceed with the command.

    Returns
    -------
    :class:`bool`
        Whether to proceed.
    """
    ask = '\nProceed ([y]/n)? '
    response = _get_input(ask).lower()
    while True:
        if response.startswith('y') or not response:
            return True
        elif response.startswith('n'):
            return False
        else:
            print('Invalid response')
            response = _get_input(ask).lower()


def _check_msl_prefix(*names):
    """Ensures that the package names start with ``msl-``.

     Parameters
     ----------
     names : :class:`tuple` of :class:`str`
        The package names.

     Returns
     -------
     :class:`list` of :class:`str`
        A list of package names with the ``msl-`` prefix.
    """
    _names = []
    for name in names:
        if name.startswith('msl-'):
            _names.append(name)
        else:
            _names.append('msl-' + name)
    return _names


def _create_install_list(names, branch, tag, update_cache, quiet=False):
    """Create a list of package names to ``install`` that are GitHub repositories_.

    Parameters
    ----------
    names : :class:`tuple` of :class:`str`
        The name of a single GitHub repository_ or multiple repository_ names.
    branch : :class:`str`
        The name of a GitHub branch.
    tag : :class:`str`
        The name of a GitHub tag.
    update_cache : :class:`bool`
        Whether to force the GitHub cache to be updated when you call this function.
    quiet : :class:`bool`, optional
        Whether to suppress the :func:`print` statements.

    Returns
    -------
    :class:`dict` of :class:`dict`
        The MSL packages to ``install``.
    """
    zip_name = _get_zip_name(branch, tag, quiet=quiet)
    if zip_name is None:
        return

    pkgs_installed = installed(quiet=quiet)
    pkgs_github = github(update_cache, quiet=quiet)

    names = _check_msl_prefix(*names)
    if not names:
        names = [pkg for pkg in pkgs_github if pkg != PKG_NAME]

    pkgs = {}
    for name in names:
        if name in pkgs_installed:
            if not quiet:
                _print_warning('The {} package is already installed'.format(name))
        elif name not in pkgs_github:
            if not quiet:
                _print_error('Cannot install {}: package not found'.format(name))
        elif branch is not None and branch not in pkgs_github[name]['branches']:
            if not quiet:
                _print_error('Cannot install {}: a "{}" branch does not exist'.format(name, branch))
        elif tag is not None and tag not in pkgs_github[name]['tags']:
            if not quiet:
                _print_error('Cannot install {}: a "{}" tag does not exist'.format(name, tag))
        else:
            pkgs[name] = pkgs_github[name]
    return pkgs


def _create_uninstall_list(names, quiet=False):
    """Create a list of package names to ``uninstall``.

    Parameters
    ----------
    names : :class:`tuple` of :class:`str`
        The name(s) of the package(s) to ``uninstall``.
    quiet : :class:`bool`, optional
        Whether to suppress the :func:`print` statements.

    Returns
    -------
    :class:`dict` of :class:`dict`
        The MSL packages to ``uninstall``.
    """

    pkgs_installed = installed(quiet=quiet)

    names = _check_msl_prefix(*names)
    if not names:
        names = [pkg for pkg in pkgs_installed if pkg != PKG_NAME]

    pkgs = {}
    for name in names:
        if name == PKG_NAME:
            if not quiet:
                _print_warning('The MSL Package Manager cannot uninstall itself. '
                              'Use "pip uninstall {}"'.format(PKG_NAME))
        elif name not in pkgs_installed:
            if not quiet:
                _print_error('Cannot uninstall {}: package not installed'.format(name))
        else:
            pkgs[name] = pkgs_installed[name]
    return pkgs




def _get_input(msg):
    """Get the input from the user (compatible with Python 2 and 3).

    Parameters
    ----------
    msg : :class:`str`
        The message to display.

    Returns
    -------
    :class:`str`
        The user's input from :attr:`sys.stdin`.

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


def _get_zip_name(branch, tag, quiet=False):
    """Returns the name of a zip file in the GitHub archive.

    Parameters
    ----------
    branch : :class:`str` or :obj:`None`
        The name of a GitHub branch.
    tag : :class:`str` or :obj:`None`
        The name of a GitHub tag.
    quiet : :class:`bool`, optional
        Whether to suppress the :func:`print` statements.

    Returns
    -------
    :class:`str`
        The name of the zip file or :obj:`None` if both `branch`
        and `tag` were specified.
    """
    if branch is not None and tag is not None:
        if not quiet:
            _print_error('Cannot specify both a branch ({}) and a tag ({})'.format(branch, tag))
        return None
    elif branch is None and tag is None:
        return 'master'
    elif branch is not None:
        return branch
    elif tag is not None:
        return tag
    else:
        assert False, 'This branch ({}) and tag ({}) combo has not been handled'.format(branch, tag)


def _inspect_github_pypi(where, update, quiet=False):
    """Inspects the temp directory for the cached json file."""

    if where == 'github':
        filename = 'msl-github-repo-cache.json'
        suffix = 'GitHub repositories'
    elif where == 'pypi':
        filename = 'msl-pypi-pkgs-cache.json'
        suffix = 'PyPI packages'
    else:
        assert False, 'Inspecting GitHub or PyPI has been configured. Got {}'.format(where)

    path = os.path.join(tempfile.gettempdir(), filename)

    cached_msg = 'Loaded the cached information about the ' + suffix

    cached_pgks = None
    if os.path.isfile(path):
        with open(path, 'r') as f:
            cached_pgks = _sort_packages(json.load(f))

    one_day = 60 * 60 * 24
    if (not update) and (cached_pgks is not None) and (time.time() < os.path.getmtime(path) + one_day):
        if not quiet:
            _print_info(cached_msg)
        return _sort_packages(cached_pgks), path, cached_msg

    return dict(), path, cached_msg


def _print_error(msg):
    """Print an error message.

    Parameters
    ----------
    msg : :class:`str`
        The message to print.
    """
    print(Style.BRIGHT + Fore.RED + msg)


def _print_info(msg):
    """Print an info message.

    Parameters
    ----------
    msg : :class:`str`
        The message to print.
    """
    print(Fore.CYAN + msg)


def _print_warning(msg):
    """Print a warning message.

    Parameters
    ----------
    msg : :class:`str`
        The message to print.
    """
    print(Fore.YELLOW + msg)


def _print_install_uninstall_message(packages, action, branch=None, tag=None):
    """Print the ``install`` or ``uninstall`` summary for what is going to happen.

    Parameters
    ----------
    packages : :class:`dict`
        The packages that are affected.
    action : :class:`str`
        The text to show in color and in upper case about what's happening.
    branch : :class:`str`, optional
        The name of a GitHub branch to use for the ``install``.
        *Only used when installing packages*.
    tag : :class:`str`, optional
        The name of a GitHub tag to use for the ``install``.
        *Only used when installing packages*.
    """
    pkgs = _sort_packages(packages)

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


def _sort_packages(pkgs):
    """Sort the MSL packages by the name of the package.

    Parameters
    ----------
    pkgs : :class:`dict`
        The MSL packages.

    Returns
    -------
    :class:`collections.OrderedDict`
        The packages sorted by name.
    """
    return OrderedDict([(k, pkgs[k]) for k in sorted(pkgs)])
