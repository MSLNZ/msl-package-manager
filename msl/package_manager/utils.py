"""
Functions for the API.

.. _packages: https://pypi.org/search/?q=%22Measurement+Standards+Laboratory+of+New+Zealand%22
.. _git: https://git-scm.com
.. _repositories: https://github.com/MSLNZ
.. _JSON: https://www.json.org/
"""
import re
import os
import sys
import json
import time
import shlex
import base64
import struct
import fnmatch
import getpass
import logging
import platform
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

_package_name_regex = re.compile(
    r'(?P<package_name>[*]?[\w-]*[*]?[\w-]*)(?P<extras_require>\[.*\])?(?P<version_requested>[<!=>~].*)?'
)


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
    :class:`dict`
        The MSL repositories_ that are available on GitHub.
    """
    packages, path = _inspect_github_pypi('github', update_cache)
    if packages:
        return packages

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
        cached_pgks = _inspect_github_pypi('github', False)[0]
        if cached_pgks:
            return cached_pgks
        return dict()

    # check if the user specified their github authorization credentials
    #
    # the os.environ option is used for testing on travis and appveyor
    # and it is not the recommended way for a user to store the credentials
    auth = os.environ.get('GITHUB_AUTHORIZATION')
    if not auth and os.path.isfile(_GITHUB_AUTH_PATH):
        with open(_GITHUB_AUTH_PATH, 'rb') as fp:
            line = fp.readline().strip()
            auth = base64.b64encode(line).decode('utf-8')

    headers = {'User-Agent': _PKG_NAME + '/Python'}
    if auth:
        headers['Authorization'] = 'Basic ' + auth

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

    # want the description to spill over to the next line in a justified manner
    # to start where the description on the previous line started
    term_w, term_h = _get_terminal_size()
    max_description_width = term_w - (w[0] + w[1]) - 2
    if w[2] > max_description_width:
        w[2] = max_description_width

    # log the results
    msg = [Fore.RESET]
    msg.append(' '.join(header[i].center(w[i]) for i in range(len(header))))
    msg.append(' '.join('-' * width for width in w))
    for p in sorted(pkgs):
        description = pkgs[p]['description'] if pkgs[p]['description'] else ''
        name_version = p.rjust(w[0]) + ' ' + pkgs[p]['version'].ljust(w[1]) + ' '
        if len(description) < w[2]:
            msg.append(name_version + description)
        else:
            # don't split a line in the in the middle of a word
            i = min(len(description) - 1, w[2])
            while description[i].strip():
                i -= 1
            msg.append(name_version + description[:i].ljust(w[2]))
            while True:
                # remove leading whitespace
                n = len(description[i:i+w[2]]) - len(description[i:i+w[2]].lstrip())
                if n > 0:
                    i += n

                iend = i + w[2]

                # check if the rest fits on 1 line
                if len(description[i:iend]) < w[2]:
                    msg.append(' ' * len(name_version) + description[i:iend].ljust(w[2]))
                    break

                # don't split a line in the in the middle of a word
                iend = min(len(description) - 1, iend)

                try:
                    description[iend]
                except IndexError:
                    raise IndexError(
                        '\ndescription={}\niend={}\nlen={}\ni={}\nw={}\nterm_w={}\nterm_h={}'.format(description, iend,
                                                                                                     len(description),
                                                                                                     i, w, term_w,
                                                                                                     term_h))

                while description[iend].strip():
                    iend -= 1
                    if iend == i:
                        iend = i + w[2]
                        break
                    try:
                        description[iend]
                    except IndexError:
                        raise IndexError('\ndescription={}\niend={}\nlen={}\ni={}\nw={}\nterm_w={}\nterm_h={}'.format(description, iend, len(description), i, w, term_w, term_h))

                msg.append(' ' * len(name_version) + description[i:iend].ljust(w[2]))
                i = iend

    log.info('\n'.join(msg))


def installed():
    """Get the MSL packages that are installed.

    Returns
    -------
    :class:`dict`
        The MSL packages that are installed.
    """
    log.debug('Getting the packages from {}'.format(os.path.dirname(sys.executable)))

    gh = github(update_cache=False)

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
    :class:`dict`
        The MSL packages_ that are available on PyPI.
    """
    packages, path = _inspect_github_pypi('pypi', update_cache)
    if packages:
        return packages

    log.debug('Getting the packages from PyPI')
    cmd = [sys.executable, '-m', 'pip', 'search', 'msl-', 'gtc', '--disable-pip-version-check']
    try:
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate()
        if err:
            lines = err.splitlines()
            if len(lines) == 1 and err.startswith(b'DEPRECATION: Python 2.7'):
                pass  # only the DEPRECATION warning was written to stderr
            else:
                raise Exception(lines[-1].decode('utf-8'))
    except Exception as e:
        log.error('Cannot connect to PyPI -- {}'.format(e))
        return _inspect_github_pypi('pypi', False)[0]
    else:
        stdout = out.decode('utf-8').strip()
        if not stdout:
            log.error('PyPI did not return any MSL packages')
            return _inspect_github_pypi('pypi', False)[0]

    pkgs = dict()
    for line in stdout.splitlines():
        match = re.match(r'(.*)\s+\((.*)\)\s+-\s+(.*)', line)
        if match and (match.group(1).lower().startswith('msl-') or match.group(1) == 'GTC'):
            pkgs[match.group(1)] = {
                'version': match.group(2),
                'description': match.group(3),
            }

    if not pkgs:
        log.critical('The regex pattern for the PyPI packages is no longer valid')
        return _inspect_github_pypi('pypi', False)[0]

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
    :class:`dict`
       The keys are the package names and the values are the version info/extra requires.
    """
    _packages = dict()
    pkgs_map = dict((p.lower(), p) for p in pkgs)
    for name in names:
        found = re.search(_package_name_regex, name.lower())
        if not found:
            continue
        result = found.groupdict()
        if not result['package_name']:
            log.error('Invalid package name {!r}'.format(name))
            continue
        found_it = False
        for prefix in ['', 'msl-']:
            for match in fnmatch.filter(pkgs_map, prefix+result['package_name']):
                found_it = True
                _packages[pkgs_map[match]] = {
                    'extras_require': result['extras_require'],
                    'version_requested': result['version_requested']
                }
        if not found_it:
            log.warning('No MSL packages match {!r}'.format(name))
    return _packages


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
    :class:`dict`
        The MSL packages to ``install``.
    """
    zip_name = _get_github_zip_name(branch, tag)
    if zip_name is None:
        return

    # keep the order of the log messages consistent: pypi -> github -> local
    pkgs_github = github(update_cache=update_cache)
    pkgs_installed = installed()

    if not names:  # e.g., the --all flag
        packages = dict((pkg, {'extras_require': None, 'version_requested': None})
                        for pkg in pkgs_github if pkg != _PKG_NAME and pkg.startswith('msl-'))
    else:
        packages = _check_wildcards_and_prefix(names, pkgs_github)

    # the name of an installed package can be different than the repo name
    repo_names = [p['repo_name'] for p in pkgs_installed.values()]

    pkgs = {}
    for name, value in packages.items():
        if name in pkgs_installed or name in repo_names:
            log.warning('The {!r} package is already installed'.format(name))
        elif name not in pkgs_github:
            log.error('Cannot install {!r} -- the package does not exist'.format(name))
        elif branch is not None and branch not in pkgs_github[name]['branches']:
            log.error('Cannot install {!r} -- a {!r} branch does not exist'.format(name, branch))
        elif tag is not None and tag not in pkgs_github[name]['tags']:
            log.error('Cannot install {!r} -- a {!r} tag does not exist'.format(name, tag))
        else:
            pkgs[name] = pkgs_github[name]
            pkgs[name]['version_requested'] = value['version_requested']
            pkgs[name]['extras_require'] = value['extras_require']
    return pkgs


def _create_uninstall_list(names):
    """Create a list of package names to ``uninstall``.

    Parameters
    ----------
    names : :class:`tuple` of :class:`str`
        The name(s) of the package(s) to ``uninstall``.

    Returns
    -------
    :class:`dict`
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

    cached_pgks = None
    if os.path.isfile(path):
        with open(path, 'r') as f:
            cached_pgks = _sort_packages(json.load(f))

    one_day = 60 * 60 * 24
    if (not update_cache) and (cached_pgks is not None) and (time.time() < os.path.getmtime(path) + one_day):
        # The installed() function also calls github() so this log message could be displayed twice.
        # Avoid seeing the following log message when the installed() function was previously called.
        if where == 'pypi' or not _ColourStreamHandler.previous_message.endswith(os.path.dirname(sys.executable)):
            log.debug('Loaded the cached information about the ' + suffix)
        return _sort_packages(cached_pgks), path

    return dict(), path


def _log_install_uninstall_message(packages, action, branch, tag, pkgs_pypi=None):
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
    pkgs_pypi : :class:`dict`
        Packages that are on PyPI. Only used when installing.
    """
    pkgs = _sort_packages(packages)

    w = [0, 0]
    for pkg, values in pkgs.items():
        if values.get('extras_require'):
            w[0] = max(w[0], len(pkg + values['extras_require']))
        else:
            w[0] = max(w[0], len(pkg))
        if values.get('version_requested'):
            w[1] = max(w[1], len(values['version_requested']))
        else:
            w[1] = max(w[1], len(values['version']))

    msg = '\n{}The following MSL packages will be {}{}{}:\n'.format(Fore.RESET, Fore.CYAN, action, Fore.RESET)
    for pkg, values in pkgs.items():
        name = pkg
        if values.get('extras_require'):
            name += values['extras_require']
        if values.get('version_requested'):
            version = values['version_requested'].replace('==', '')
        else:
            version = '' if branch is not None or tag is not None else values['version']
        msg += '\n  {}  {} '.format(name.ljust(w[0]), version.ljust(w[1]))
        if action == 'REMOVED':
            continue
        if branch is not None:
            msg += ' [branch:{}]'.format(branch)
        elif tag is not None:
            msg += ' [tag:{}]'.format(tag)
        elif pkg in pkgs_pypi:
            msg += ' [PyPI]'
        else:
            msg += ' [GitHub]'

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
    return collections.OrderedDict([(u'{}'.format(k), pkgs[k]) for k in sorted(pkgs)])


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

    previous_message = ''

    def emit(self, record):
        _ColourStreamHandler.previous_message = record.getMessage()
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


def _get_terminal_size():
    """
    Taken from https://gist.github.com/jtriley/1108174

    getTerminalSize()
     - get width and height of console
     - works on linux,os x,windows,cygwin(windows)
     originally retrieved from:
     http://stackoverflow.com/questions/566746/how-to-get-console-window-width-in-python
    """
    current_os = platform.system()
    tuple_xy = None
    if current_os == 'Windows':
        tuple_xy = _get_terminal_size_windows()
        if tuple_xy is None:
            tuple_xy = _get_terminal_size_tput()
            # needed for window's python in cygwin's xterm!
    if current_os in ['Linux', 'Darwin'] or current_os.startswith('CYGWIN'):
        tuple_xy = _get_terminal_size_linux()
    if tuple_xy is None:
        tuple_xy = (80, 25)  # default value
    return tuple_xy


def _get_terminal_size_windows():
    try:
        from ctypes import windll, create_string_buffer
        # stdin handle is -10
        # stdout handle is -11
        # stderr handle is -12
        h = windll.kernel32.GetStdHandle(-12)
        csbi = create_string_buffer(22)
        res = windll.kernel32.GetConsoleScreenBufferInfo(h, csbi)
        if res:
            (bufx, bufy, curx, cury, wattr,
             left, top, right, bottom,
             maxx, maxy) = struct.unpack("hhhhHhhhhhh", csbi.raw)
            return right - left, bottom - top
    except:
        pass


def _get_terminal_size_tput():
    # get terminal width
    # src: http://stackoverflow.com/questions/263890/how-do-i-find-the-width-height-of-a-terminal-window
    try:
        cols = int(subprocess.check_call(shlex.split('tput cols')))
        rows = int(subprocess.check_call(shlex.split('tput lines')))
        return cols, rows
    except:
        pass


def _get_terminal_size_linux():
    def ioctl_GWINSZ(fd):
        try:
            import fcntl
            import termios
            cr = struct.unpack('hh', fcntl.ioctl(fd, termios.TIOCGWINSZ, '1234'))
            return cr
        except:
            pass

    cr = ioctl_GWINSZ(0) or ioctl_GWINSZ(1) or ioctl_GWINSZ(2)
    if not cr:
        try:
            fd = os.open(os.ctermid(), os.O_RDONLY)
            cr = ioctl_GWINSZ(fd)
            os.close(fd)
        except:
            pass
    if not cr:
        try:
            cr = (os.environ['LINES'], os.environ['COLUMNS'])
        except:
            return None
    return int(cr[1]), int(cr[0])
