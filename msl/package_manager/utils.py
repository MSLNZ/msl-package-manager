"""
Functions for the API.

.. _packages: https://pypi.org/search/?q=msl-
.. _git: https://git-scm.com
.. _repositories: https://github.com/MSLNZ
.. _JSON: https://www.json.org/
"""
import re
import os
import sys
import json
import time
import base64
import fnmatch
import getpass
import logging
import datetime
import tempfile
import threading
import subprocess
import collections
import pkg_resources
try:
    from importlib import reload
except ImportError:
    from imp import reload  # Python 2
try:
    from urllib2 import urlopen, Request, HTTPError  # Python 2
except ImportError:
    from urllib.request import urlopen, Request, HTTPError

from colorama import Fore, Style, Back, init

from . import _PKG_NAME

_NUM_QUIET = 0
_IS_WINDOWS = sys.platform in {'win32', 'cygwin'}

if not os.path.isdir(os.path.join(os.path.expanduser('~'), '.msl')):
    os.mkdir(os.path.join(os.path.expanduser('~'), '.msl'))

_GITHUB_AUTH_PATH = os.path.join(os.path.expanduser('~'), '.msl', '.mslpm-github-auth')


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
        except IOError as err:
            log.error('Error requesting {} from GitHub -- {}'.format(url, err))
        else:
            return json.loads(response.read().decode('utf-8'))

    def fetch_latest_release(repo_name):
        reply = fetch('/repos/MSLNZ/{}/releases/latest'.format(repo_name))
        if reply is None:
            val = None
        elif reply:
            val = reply['name'] if reply['name'] else reply['tag_name']
            val = val.replace('v', '')
        else:
            val = ''
        pkgs[repo_name]['version'] = val

    def fetch_tags(repo_name):
        reply = fetch('/repos/MSLNZ/{}/tags'.format(repo_name))
        if reply is None:
            val = None
        else:
            val = [tag['name'] for tag in reply]
        pkgs[repo_name]['tags'] = val

    def fetch_branches(repo_name):
        reply = fetch('/repos/MSLNZ/{}/branches'.format(repo_name))
        if reply is None:
            val = None
        else:
            val = [branch['name'] for branch in reply]
        pkgs[repo_name]['branches'] = val

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
        if repo['language'] == 'Python':
            pkgs[repo['name']] = {'description': repo['description']}

    threads = [
        threading.Thread(target=fcn, args=(repo_name,))
        for fcn in [fetch_latest_release, fetch_tags, fetch_branches]
        for repo_name in pkgs
    ]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    # check if there was an error in one of the threads
    for repo_name, sub_dict in pkgs.items():
        for key, value in sub_dict.items():
            if value is None:
                log.warning('The {!r} repository does not have a {!r}'.format(repo_name, key))

    with open(path, 'w') as fp:
        json.dump(pkgs, fp)

    return _sort_packages(pkgs)


def info(from_github=False, from_pypi=False, update_cache=False, as_json=False):
    """Show the information about MSL packages.

    The information about the packages can be either those that are installed or
    those that are available as repositories_ on GitHub or as packages_ on PyPI.

    The default action is to show the information about the MSL packages that are installed.

    Parameters
    ----------
    from_github : :class:`bool`, optional
        Whether to show the MSL repositories_ that are available on GitHub.
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
    as_json : :class:`bool`, optional
        Whether to show the information in JSON_ format. If enabled then the information
        about the MSL repositories_ includes additional information about the branches
        and tags.
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

    if as_json:
        log.info(Fore.RESET)
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
    msg = [Fore.RESET]
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

    log.disabled = True
    gh = github(update_cache=False)
    log.disabled = False

    # refresh the working_set
    reload(pkg_resources)

    pkgs = {}
    for dist in pkg_resources.working_set:
        repo_name = None
        if dist.project_name in gh:  # the installed name might be different than the repo name
            repo_name = dist.project_name

        description = ''
        if dist.has_metadata(dist.PKG_INFO):
            for line in dist.get_metadata_lines(dist.PKG_INFO):
                if line.startswith('Summary:'):
                    description = line[8:].strip()  # can be UNKNOWN
                elif line.startswith('Home-page:') and 'github.com/MSLNZ' in line:
                    repo_name = line.split('/')[-1]
                    if description:
                        break

        if repo_name is None:
            continue

        if description == 'UNKNOWN':
            description = gh[repo_name]['description']

        pkgs[dist.project_name] = {
            'version': dist.version,
            'description': description,
            'repo_name': repo_name
        }

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

    log.debug('Getting the packages from PyPI')
    command = [sys.executable, '-m', 'pip', 'search', 'msl-']
    options = ['--disable-pip-version-check'] + ['--quiet'] * _NUM_QUIET
    try:
        p2 = subprocess.Popen(command + options, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p2.communicate()
        if err:
            raise Exception(err.splitlines()[-1].decode())
    except Exception as e:
        log.error('Cannot connect to PyPI -- {}'.format(e))
        if cached_pgks:
            log.info(cached_msg)
            return cached_pgks
        return dict()
    else:
        stdout = out.decode('utf-8').strip()

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
            log.warning('Invalid kwarg {!r}'.format(item))


def _check_wildcards_and_prefix(names, pkgs):
    """Check if a Unix shell-style wildcard was used or if the package
    name starts with the msl- prefix.

    Parameters
    ----------
    names : :class:`tuple` of :class:`str`
       The package names.
    pkgs : :class:`dict`
       The GitHub repositories or the installed packages.

    Returns
    -------
    :class:`set` of :class:`str`
       A set of package names.
    """
    _names = set()
    pkgs_map = dict((p.lower(), p) for p in pkgs)
    for name in names:
        name = name.lower()
        for prefix in ['', 'msl-']:
            for match in fnmatch.filter(pkgs_map, prefix+name):
                _names.add(pkgs_map[match])
    return _names


def _create_install_list(names, branch, tag, update_cache):
    """Create a list of package names to ``install`` that are GitHub repositories_.

    Parameters
    ----------
    names : :class:`tuple` of :class:`str`
        The name of a single GitHub repository or multiple repository names.
    branch : :class:`str` or :data:`None`
        The name of a GitHub branch.
    tag : :class:`str` or :data:`None`
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
    pkgs_github = github(update_cache=update_cache)

    if not names:  # e.g., the --all flag
        names = [pkg for pkg in pkgs_github if pkg != _PKG_NAME and pkg.startswith('msl-')]
    else:
        names = _check_wildcards_and_prefix(names, pkgs_github)

    # the name of an installed package can be different than the repo name
    repo_names = [p['repo_name'] for p in pkgs_installed.values()]

    pkgs = {}
    for name in names:
        if name in pkgs_installed or name in repo_names:
            log.warning('The {!r} package is already installed.'.format(name))
        elif name not in pkgs_github:
            log.error('Cannot install {!r}. The package is not found.'.format(name))
        elif branch is not None and branch not in pkgs_github[name]['branches']:
            log.error('Cannot install {!r}. A {!r} branch does not exist.'.format(name, branch))
        elif tag is not None and tag not in pkgs_github[name]['tags']:
            log.error('Cannot install {!r}. A {!r} tag does not exist.'.format(name, tag))
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

    if not names:
        names = [pkg for pkg in pkgs_installed if pkg != _PKG_NAME]
    else:
        names = _check_wildcards_and_prefix(names, pkgs_installed)

    pkgs = {}
    for name in names:
        if name == _PKG_NAME:
            log.warning('The MSL Package Manager cannot uninstall itself. '
                        'Use "pip uninstall {}"'.format(_PKG_NAME))
        elif name not in pkgs_installed:
            log.error('Cannot uninstall {!r}: The package is not installed.'.format(name))
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
        log.error('Cannot specify both a branch ({}) and a tag ({}).'.format(branch, tag))
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

    msg = '\n{}The following MSL packages will be {}{}{}:\n'.format(Fore.RESET, Fore.CYAN, action, Fore.RESET)
    for pkg, values in pkgs.items():
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
