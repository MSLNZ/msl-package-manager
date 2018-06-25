"""
Functions for the API.

.. _packages: https://pypi.org/search/?q=msl-
.. _git: https://git-scm.com
.. _repositories: https://github.com/MSLNZ
"""
import re
import os
import sys
import json
import time
import base64
import getpass
import logging
import datetime
import tempfile
import subprocess
import collections
import pkg_resources
from multiprocessing.pool import ThreadPool
try:
    import imp as importlib
except ImportError:
    import importlib
try:
    from urllib2 import urlopen, Request, HTTPError  # Python 2
except ImportError:
    from urllib.request import urlopen, Request, HTTPError

from colorama import Fore, Style, Back, init

from . import _PKG_NAME

_NUM_QUIET = 0

_GITHUB_AUTH_PATH = os.path.join(os.path.expanduser('~'), '.msl-package-manager-github-auth')


def get_email():
    """Try to determine the user's email address.

    If git_ is installed then it returns the ``user.email`` parameter from the user's git_
    account to use as the user's email address. If git_ is not installed then returns
    :data:`None`.

    Returns
    -------
    :class:`str` or :data:`None`
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


def github(update_cache=False):
    """Get the MSL repositories_ that are available on GitHub.

    Parameters
    ----------
    update_cache : :class:`bool`, optional
        The information about the repositories_ that are available on GitHub are
        cached to use for subsequent calls to this function. After 24 hours the
        cache is automatically updated. Set `update_cache` to be :data:`True`
        to force the cache to be updated when you call this function.

    Returns
    -------
    :class:`dict` of :class:`dict`
        The MSL repositories_ that are available on GitHub.
    """
    cached_pgks, path, cached_msg = _inspect_github_pypi('github', update_cache)
    if cached_pgks:
        return cached_pgks

    def fetch(url_suffix):
        url = 'https://api.github.com' + url_suffix
        try:
            response = urlopen(Request(url, headers=headers))
        except HTTPError as err:
            if err.code == 401:
                msg = 'You have provided invalid Authorization information'
            elif err.code == 404:
                # Could get this error if the URL does not exist.
                # For example, getting .../releases/latest might not exist
                # if no releases for the repo are available yet.
                # This not an error type that we care about.
                return dict()
            elif err.code == 403:
                reply = fetch('/rate_limit')
                if reply['resources']['core']['remaining'] == 0:
                    reset = int(reply['resources']['core']['reset'])
                    hms = datetime.datetime.fromtimestamp(reset).strftime('%H:%M:%S')
                    msg = 'The GitHub API rate limit was exceeded. Retry again at {} or create a file\n' \
                          'with your GitHub authorization credentials to increase your rate limit. Run\n' \
                          '"msl authorize --help" for more details.'.format(hms)
                else:
                    msg = 'Unhandled HTTP error 403. The rate_limit was not reached...'
            else:
                msg = 'Unhandled HTTP error...'

            log.error('Error requesting {} from GitHub -- {}\n{}'.format(url, err, msg))

        else:
            return json.loads(response.read().decode('utf-8'))

    def fetch_latest_release(name):
        reply = fetch('/repos/MSLNZ/{}/releases/latest'.format(name))
        if reply is None:
            return name, None
        if reply:
            latest = reply['name'] if reply['name'] else reply['tag_name']
        else:
            latest = ''
        return name, latest.replace('v', '')

    def fetch_tags(name):
        reply = fetch('/repos/MSLNZ/{}/tags'.format(name))
        if reply is None:
            return name, None
        return name, [tag['name'] for tag in reply]

    def fetch_branches(name):
        reply = fetch('/repos/MSLNZ/{}/branches'.format(name))
        if reply is None:
            return name, None
        return name, [branch['name'] for branch in reply]

    def reload_cache():
        cached_pgks, path, cached_msg = _inspect_github_pypi('github', False)
        if cached_pgks:
            return cached_pgks
        return dict()

    # check if the user specified their github authorization credentials in the default file
    try:
        with open(_GITHUB_AUTH_PATH, 'rb') as fp:
            auth = fp.readline().strip()
    except IOError:
        headers = dict()
    else:
        headers = {
            'Authorization': 'Basic ' + base64.b64encode(auth).decode('utf-8'),
            'User-Agent': 'msl-package-manager/Python'
        }

    log.debug('Getting the repositories from GitHub')
    repos = fetch('/orgs/MSLNZ/repos')
    if not repos:
        # even though updating the cache was requested just reload the cached data
        # because github cannot be connected to right now
        return reload_cache()

    pkgs = dict()
    for repo in repos:
        name = repo['name']
        if name.startswith('msl-'):
            pkgs[name] = {'description': repo['description']}

    version_thread = ThreadPool(len(pkgs)).imap_unordered(fetch_latest_release, pkgs)
    tags_thread = ThreadPool(len(pkgs)).imap_unordered(fetch_tags, pkgs)
    branches_thread = ThreadPool(len(pkgs)).imap_unordered(fetch_branches, pkgs)
    for key, thread in (('version', version_thread), ('tags', tags_thread), ('branches', branches_thread)):
        for repo_name, value in thread:
            if value is None:  # then there was an error in one of the threads
                return reload_cache()
            pkgs[repo_name][key] = value

    with open(path, 'w') as fp:
        json.dump(pkgs, fp)

    return _sort_packages(pkgs)


def info(from_github=False, detailed=False, from_pypi=False, update_cache=False):
    """Show the information about MSL packages.

    The information about the packages can be either those that are installed or
    those that are available as repositories_ on GitHub or as packages_ on PyPI.

    The default action is to show the information about the MSL packages that are installed.

    Parameters
    ----------
    from_github : :class:`bool`, optional
        Whether to show the MSL repositories_ that are available on GitHub.
    detailed : :class:`bool`, optional
        Whether to show **detailed** information about the MSL repositories_
        (i.e., displays additional information about the branches and tags).
        Only used if `from_github` is :data:`True`.
    from_pypi : :class:`bool`, optional
        Whether to show the MSL packages_ that are available on PyPI.
    update_cache : :class:`bool`, optional
        The information about the MSL packages_ that are available on PyPI and about
        the repositories_ that are available on GitHub are cached to use for subsequent
        calls to this function. After 24 hours the cache is automatically updated. Set
        `update_cache` to be :data:`True` to force the cache to be updated when you call
        this function. If `from_github` is :data:`True` then the cache for the
        repositories_ is updated. If `from_pypi` is :data:`True` then the cache for the
        packages_ is updated.
    """
    if from_github:
        typ, pkgs = 'Repository', github(update_cache=update_cache)
        if not pkgs:
            return
    elif from_pypi:
        typ, pkgs = 'PyPI Package', pypi(update_cache=update_cache)
        if not pkgs:
            return
    else:
        typ, pkgs = 'Package', installed()

    if detailed and from_github:
        log.info(json.dumps(pkgs, indent=2))
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

    # log the results
    msg = ['']
    msg.append(' '.join(header[i].ljust(w[i]) for i in range(len(header))))
    msg.append(' '.join('-' * width for width in w))
    for p in sorted(pkgs):
        description = pkgs[p]['description'] if pkgs[p]['description'] else ''
        msg.append(p.ljust(w[0]) + ' ' + pkgs[p]['version'].ljust(w[1]) + ' ' + description.ljust(w[2]))
    log.info('\n'.join(msg))


def installed():
    """Get the MSL packages that are installed.

    Returns
    -------
    :class:`dict` of :class:`dict`
        The MSL packages that are installed.
    """
    log.debug('Getting the packages from {}'.format(os.path.dirname(sys.executable)))

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


def pypi(update_cache=False):
    """Get the MSL packages_ that are available on PyPI.

    Parameters
    ----------
    update_cache : :class:`bool`, optional
        The information about the MSL packages_ that are available on PyPI are
        cached to use for subsequent calls to this function. After 24 hours the
        cache is automatically updated. Set `update_cache` to be :data:`True`
        to force the cache to be updated when you call this function.

    Returns
    -------
    :class:`dict` of :class:`dict`
        The MSL packages_ that are available on PyPI.
    """
    cached_pgks, path, cached_msg = _inspect_github_pypi('pypi', update_cache)
    if cached_pgks:
        return cached_pgks

    try:
        log.debug('Getting the packages from PyPI')
        command = [sys.executable, '-m', 'pip', 'search', 'msl-']
        options = ['--quiet'] * _NUM_QUIET
        p2 = subprocess.Popen(command + options, stdout=subprocess.PIPE)
        stdout = p2.communicate()[0].decode('utf-8').strip()
    except Exception as err:
        log.error('Cannot connect to PyPI -- {}'.format(err))
        if cached_pgks is not None:
            log.info(cached_msg)
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


def set_log_level(level):
    """Set the logging :py:ref:`level <levels>`.

    Parameters
    ----------
    level : :class:`int`
        A value from one of the :py:ref:`levels`.
    """
    global _NUM_QUIET

    if level <= logging.WARNING:
        _NUM_QUIET = 0
    elif level == logging.ERROR:
        _NUM_QUIET = 1
    elif level == logging.CRITICAL:
        _NUM_QUIET = 2
    else:
        _NUM_QUIET = 3

    log.setLevel(level)


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
            log.info('Invalid response')
            response = _get_input(ask).lower()


def _check_kwargs(kwargs, allowed):
    for item in kwargs:
        if item not in allowed:
            log.warning('Invalid kwarg "{}"'.format(item))


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


def _create_install_list(names, branch, tag, update_cache):
    """Create a list of package names to ``install`` that are GitHub repositories_.

    Parameters
    ----------
    names : :class:`tuple` of :class:`str`
        The name of a single GitHub repository or multiple repository names.
    branch : :class:`str`
        The name of a GitHub branch.
    tag : :class:`str`
        The name of a GitHub tag.
    update_cache : :class:`bool`
        Whether to force the GitHub cache to be updated when you call this function.

    Returns
    -------
    :class:`dict` of :class:`dict`
        The MSL packages to ``install``.
    """
    zip_name = _get_github_zip_name(branch, tag)
    if zip_name is None:
        return

    pkgs_installed = installed()
    pkgs_github = github(update_cache)

    names = _check_msl_prefix(*names)
    if not names:
        names = [pkg for pkg in pkgs_github if pkg != _PKG_NAME]

    pkgs = {}
    for name in names:
        if name in pkgs_installed:
            log.warning('The {} package is already installed'.format(name))
        elif name not in pkgs_github:
            log.error('Cannot install {}: package not found'.format(name))
        elif branch is not None and branch not in pkgs_github[name]['branches']:
            log.error('Cannot install {}: a "{}" branch does not exist'.format(name, branch))
        elif tag is not None and tag not in pkgs_github[name]['tags']:
            log.error('Cannot install {}: a "{}" tag does not exist'.format(name, tag))
        else:
            pkgs[name] = pkgs_github[name]
    return pkgs


def _create_uninstall_list(names):
    """Create a list of package names to ``uninstall``.

    Parameters
    ----------
    names : :class:`tuple` of :class:`str`
        The name(s) of the package(s) to ``uninstall``.

    Returns
    -------
    :class:`dict` of :class:`dict`
        The MSL packages to ``uninstall``.
    """

    pkgs_installed = installed()

    names = _check_msl_prefix(*names)
    if not names:
        names = [pkg for pkg in pkgs_installed if pkg != _PKG_NAME]

    pkgs = {}
    for name in names:
        if name == _PKG_NAME:
            log.warning('The MSL Package Manager cannot uninstall itself. '
                        'Use "pip uninstall {}"'.format(_PKG_NAME))
        elif name not in pkgs_installed:
            log.error('Cannot uninstall {}: package not installed'.format(name))
        else:
            pkgs[name] = pkgs_installed[name]
    return pkgs


def _get_input(msg):
    """Get input from the user.

    Parameters
    ----------
    msg : :class:`str`
        The message to display.

    Returns
    -------
    :class:`str`
        The user's input from :attr:`sys.stdin`.
    """
    try:
        return raw_input(msg)  # Python 2
    except NameError:
        return input(msg)


def _get_github_zip_name(branch, tag):
    """Returns the name of a zip file in the GitHub archive.

    Parameters
    ----------
    branch : :class:`str` or :data:`None`
        The name of a GitHub branch.
    tag : :class:`str` or :data:`None`
        The name of a GitHub tag.

    Returns
    -------
    :class:`str` or :data:`None`
        The name of the zip file or :data:`None` if both `branch`
        and `tag` were specified.
    """
    if branch is not None and tag is not None:
        log.error('Cannot specify both a branch ({}) and a tag ({})'.format(branch, tag))
        return None
    elif branch is None and tag is None:
        return 'master'
    elif branch is not None:
        return branch
    elif tag is not None:
        return tag
    else:
        assert False, 'This branch ({}) and tag ({}) combo has not been handled'.format(branch, tag)


def _inspect_github_pypi(where, update_cache):
    """Inspects the temp directory for the cached json file.

    Parameters
    ----------
    where : :class:`str`
        Either 'github' or 'pypi'
    update_cache : :class:`bool`
        Whether to update the cache.

    Returns
    -------
    :class:`dict`
        The packages
    :class:`str`
        The path to the cached files.
    :class:`str`
        A message about the where the cached data comes from.
    """
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
    if (not update_cache) and (cached_pgks is not None) and (time.time() < os.path.getmtime(path) + one_day):
        log.debug(cached_msg)
        return _sort_packages(cached_pgks), path, cached_msg

    return dict(), path, cached_msg


def _log_install_uninstall_message(packages, action, branch, tag):
    """Print the ``install`` or ``uninstall`` summary for what is going to happen.

    Parameters
    ----------
    packages : :class:`dict`
        The packages that are affected.
    action : :class:`str`
        The text to show in color and in upper case about what's happening.
    branch : :class:`str` or :data:`None`
        The name of a GitHub branch to use for the ``install``.
        *Only used when installing packages*.
    tag : :class:`str` or :data:`None`
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

    log.info(msg)


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
    return collections.OrderedDict([(k, pkgs[k]) for k in sorted(pkgs)])


class _ColourStreamHandler(logging.StreamHandler):
    """A SteamHandler that is compatible with colorama."""

    COLOURS = {
        'DEBUG': Fore.CYAN,
        'INFO': '',
        'WARN': Fore.YELLOW,
        'WARNING': Fore.YELLOW,
        'ERROR': Style.BRIGHT + Fore.RED,
        'CRIT': Back.RED + Fore.WHITE,
        'CRITICAL': Back.RED + Fore.WHITE
    }

    def emit(self, record):
        try:
            message = self.format(record)
            self.stream.write(self.COLOURS[record.levelname] + message)
            self.stream.write(getattr(self, 'terminator', '\n'))
            self.flush()
        except:
            self.handleError(record)


def _getLogger(name=None, fmt='%(message)s'):
    """Create the default stream logger"""
    init(autoreset=True)  # initialize colorama
    logger = logging.getLogger(name)
    handler = _ColourStreamHandler()
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(logging.Formatter(fmt))
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
    return logger


log = _getLogger(_PKG_NAME)
