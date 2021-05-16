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
import textwrap
import platform
import datetime
import tempfile
import threading
import subprocess
import collections
import pkg_resources
try:
    from importlib import reload
    from urllib.request import urlopen, Request, HTTPError, URLError
except ImportError:  # then Python 2
    from imp import reload
    from urllib2 import urlopen, Request, HTTPError, URLError

from colorama import Fore, Style, Back, init

from . import _PKG_NAME

_pip_quiet = 0
_IS_WINDOWS = sys.platform in {'win32', 'cygwin'}

_HOME_DIR = os.path.join(os.path.expanduser('~'), '.msl')
if not os.path.isdir(_HOME_DIR):
    os.mkdir(_HOME_DIR)

_GITHUB_AUTH_PATH = os.path.join(_HOME_DIR, '.mslpm-github-auth')

_package_name_regex = re.compile(
    r'(?P<package_name>[*]?[\w-]*[*]?[\w-]*)(?P<extras_require>\[.*\])?(?P<version_requested>[<!=>~].*)?'
)

try:
    subprocess.check_output(['git', '--version'])
except:
    has_git = False
else:
    has_git = True


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
    if has_git:
        try:
            email = subprocess.check_output(['git', 'config', 'user.email'])
        except subprocess.CalledProcessError:
            pass
        else:
            return email.strip().decode('utf-8')


def get_username():
    """Determine the name of the user.

    If git_ is installed then it returns the ``user.name`` parameter from the user's git_
    account. If git_ is not installed or if the ``user.name`` parameter does not exist
    then :func:`getpass.getuser` is used to determine the username.

    Returns
    -------
    :class:`str`
        The user's name.
    """
    if has_git:
        try:
            uname = subprocess.check_output(['git', 'config', 'user.name'])
        except subprocess.CalledProcessError:
            pass
        else:
            return uname.strip().decode('utf-8')
    return getpass.getuser()


def github(update_cache=False):
    """Get the information about the MSL repositories_ that are available on GitHub.

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
        The information about the MSL repositories_ that are available on GitHub.
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
        except URLError as err:
            log.error('Error requesting {} from GitHub -- {}'.format(url, err))
        else:
            return json.loads(response.read().decode('utf-8'))

    def fetch_latest_release(repo_name):
        reply = fetch('/repos/MSLNZ/{}/releases/latest'.format(repo_name))
        if reply:
            val = reply['name'] if reply['name'] else reply['tag_name']
            val = val.replace('v', '')
        else:
            val = ''
        pkgs[repo_name]['version'] = val

    def fetch_tags(repo_name):
        reply = fetch('/repos/MSLNZ/{}/tags'.format(repo_name))
        pkgs[repo_name]['tags'] = [tag['name'] for tag in reply] if reply else []

    def fetch_branches(repo_name):
        reply = fetch('/repos/MSLNZ/{}/branches'.format(repo_name))
        pkgs[repo_name]['branches'] = [branch['name'] for branch in reply] if reply else []

    def reload_cache():
        cached_pgks = _inspect_github_pypi('github', False)[0]
        if cached_pgks:
            return cached_pgks
        return dict()

    # check if the user specified their github authorisation credentials
    #
    # the os.environ option is used for CI testing and it is not the
    # recommended way for a user to store their credentials
    auth = os.environ.get('MSL_PM_GITHUB_AUTHORISATION')
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
            if repo['description'] is None:
                repo['description'] = ''
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

    with open(path, 'w') as fp:
        json.dump(pkgs, fp)

    return _sort_packages(pkgs)


def info(from_github=False, from_pypi=False, update_cache=False, as_json=False):
    """Show information about MSL packages.

    The information about the packages can be either those that are installed or
    those that are available as repositories_ on GitHub or as packages_ on PyPI.

    The default action is to show the information about the MSL packages that are installed.

    Parameters
    ----------
    from_github : :class:`bool`, optional
        Whether to show the information about the MSL repositories_ that are available on GitHub.
    from_pypi : :class:`bool`, optional
        Whether to show the information about the MSL packages_ that are available on PyPI.
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
            max(w[2], len(pkgs[p]['description']))
        ]

    if 'PYCHARM_HOSTED' not in os.environ:
        # if not executing within the PyCharm IDE then the description
        # should wrap to the next line and begin where the description
        # on the previous line started
        term_w, term_h = _get_terminal_size()
        max_description_width = max(len(header[2]), term_w - (w[0] + w[1]) - 2)
        if w[2] > max_description_width:
            w[2] = max_description_width

    # log the results
    msg = [Fore.RESET]
    msg.append(' '.join(header[i].center(w[i]) for i in range(len(header))))
    msg.append(' '.join('-' * width for width in w))
    for p in sorted(pkgs):
        description = pkgs[p]['description']
        name_version = p.rjust(w[0]) + ' ' + pkgs[p]['version'].ljust(w[1]) + ' '
        if not description:
            msg.append(name_version)
        else:
            padding = ' ' * len(name_version)
            wrapped_lines = textwrap.wrap(description, width=w[2])
            msg.append(name_version + wrapped_lines[0])
            for line in wrapped_lines[1:]:
                msg.append(padding + line)

    log.info('\n'.join(msg))


def installed():
    """Get the information about the MSL packages that are installed.

    Returns
    -------
    :class:`dict`
        The information about the MSL packages that are installed.
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
        requires = []
        if dist.has_metadata(dist.PKG_INFO):
            for line in dist.get_metadata_lines(dist.PKG_INFO):
                if line.startswith('Summary:'):
                    description = line[8:].strip()  # can be UNKNOWN
                elif line.startswith('Home-page:') and 'github.com/MSLNZ' in line:
                    repo_name = line.split('/')[-1]
                    requires = dist.requires()
                    if description:
                        break

        if repo_name is None:
            continue

        if description == 'UNKNOWN':
            description = gh[repo_name]['description']

        pkgs[dist.project_name] = {
            'version': dist.version,
            'description': description,
            'repo_name': repo_name,
            'requires': requires,
        }

    return _sort_packages(pkgs)


def outdated_pypi_packages(msl_installed=None):
    """Check PyPI for all non-MSL packages that are outdated.

    .. versionadded:: 2.5.0

    Parameters
    ----------
    msl_installed : :class:`dict`, optional
        The MSL packages that are installed. If not specified
        then calls :func:`installed` to determine the
        installed packages.

    Returns
    -------
    :class:`dict`
        The information about the PyPI packages that are outdated.
    """
    pkgs_to_update = dict()
    try:
        output = subprocess.check_output([sys.executable, '-m', 'pip', 'list', '--outdated'])
    except subprocess.CalledProcessError as e:
        log.error('ERROR: "pip list --outdated" invalid -> {}'.format(e))
        return pkgs_to_update

    lines = output.decode().splitlines()
    if not lines:
        return pkgs_to_update

    header = [item.lower() for item in lines[0].split()]
    if header[:3] != ['package', 'version', 'latest']:
        log.error('ERROR: pip has changed the structure of the outdated packages')
        return pkgs_to_update

    # ignore lines[1] since it is a bunch of '-'
    outdated_packages = [dict(zip(header, line.split())) for line in lines[2:]]

    if not msl_installed:
        msl_installed = installed()

    for msl_project_name, item in msl_installed.items():
        for outdated in outdated_packages:
            package = outdated['package']
            if package == 'pip':
                continue

            for msl_requirement in item['requires']:
                if msl_requirement.project_name.startswith(package):
                    # cannot update a package to the latest version
                    # on PyPI if the installed MSL package specifies
                    # that it only supports a specific version
                    if msl_requirement.specifier:
                        specifier = str(msl_requirement.specifier)
                        if package in pkgs_to_update:
                            if specifier not in pkgs_to_update[package]['version']:
                                # multiple version constraints
                                pkgs_to_update[package]['version'] += ','+specifier
                        else:
                            pkgs_to_update[package] = {
                                'installed_version': outdated['version'],
                                'using_pypi': True,
                                'extras_require': '',
                                'version': specifier,
                                'repo_name': '',
                            }

            if package not in pkgs_to_update and package not in msl_installed:
                pkgs_to_update[package] = {
                    'installed_version': outdated['version'],
                    'using_pypi': True,
                    'extras_require': '',
                    'version': outdated['latest'],
                    'repo_name': '',
                }

    return _sort_packages(pkgs_to_update)


def pypi(update_cache=False):
    """Get the information about the MSL packages_ that are available on PyPI.

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
        The information about the MSL packages_ that are available on PyPI.
    """
    packages, path = _inspect_github_pypi('pypi', update_cache)
    if packages:
        return packages

    def request(endpoint):
        # send a request to the PyPI endpoint
        try:
            reply = urlopen(Request('https://pypi.org' + endpoint, headers=headers))
        except URLError as err:
            log.error('Error requesting {!r} -- {}'.format(endpoint, err))
        else:
            return reply.read().decode('utf-8')

    def use_json_api():
        # use the JSON API as a backup way to get the package information from PyPI
        projects = ('msl-package-manager', 'msl-network', 'msl-loadlib', 'GTC', 'Quantity-Value')
        for project in projects:
            reply = request('/pypi/{}/json'.format(project))
            if reply:
                info = json.loads(reply).get('info')
                if info:
                    pkgs[project] = {
                        'version': info.get('version', 'UNKNOWN'),
                        'description': info.get('summary', 'UNKNOWN')
                    }

    pkgs = dict()
    log.debug('Getting the packages from PyPI')
    headers = {'User-Agent': _PKG_NAME + '/Python'}

    # use the /search endpoint before the /json endpoint since searching does not
    # depend on knowing in advance what MSL packages are available on PyPI
    reply = request('/search/?q=%22Measurement+Standards+Laboratory+of+New+Zealand%22&o=')
    if reply:
        items = re.findall(
            r'<span class="package-snippet__name">(?P<name>.+)</span>\s+'
            r'<span class="package-snippet__version">(?P<version>.+)</span>\s+'
            r'<span class="package-snippet__released">.+\s+(?P<released>.+)\s+.+\s+.+\s+'
            r'<p class="package-snippet__description">(?P<description>.+)</p>',
            reply,
        )
        for item in items:
            name, version, released, description = item
            pkgs[name] = {
                'version': version,
                'description': description,
            }
        if not pkgs:
            log.critical('PyPI regex pattern is invalid for the /search endpoint')
            use_json_api()
    else:
        use_json_api()

    if not pkgs:
        return _inspect_github_pypi('pypi', False)[0]

    with open(path, mode='wt') as fp:
        json.dump(pkgs, fp)

    return _sort_packages(pkgs)


def set_log_level(level):
    """Set the logging :py:ref:`level <levels>`.

    Parameters
    ----------
    level : :class:`int`
        A value from one of the :py:ref:`levels`.
    """
    global _pip_quiet

    if level <= logging.INFO:
        _pip_quiet = 0
    elif level == logging.WARNING:
        _pip_quiet = 1
    elif level == logging.ERROR:
        _pip_quiet = 2
    else:
        _pip_quiet = 3

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


def _create_install_list(names, branch, commit, tag, update_cache):
    """Create a list of package names to ``install`` that are GitHub repositories_.

    Parameters
    ----------
    names : :class:`tuple` of :class:`str`
        The name of a single GitHub repository or multiple repository names.
    branch : :class:`str` or :data:`None`
        The name of a git branch.
    commit : :class:`str` or :data:`None`
        The hash value of a git commit.
    tag : :class:`str` or :data:`None`
        The name of a git tag.
    update_cache : :class:`bool`
        Whether to force the GitHub cache to be updated when you call this function.

    Returns
    -------
    :class:`dict`
        The MSL packages to ``install``.
    """
    github_suffix = _get_github_url_suffix(branch, commit, tag)
    if github_suffix is None:
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
            log.warning('The {!r} package is already installed -- use the update command'.format(name))
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


def _get_github_url_suffix(branch=None, commit=None, tag=None):
    """Returns the URL suffix.

    Parameters
    ----------
    branch : :class:`str` or :data:`None`
        The name of a git branch.
    commit : :class:`str` or :data:`None`
        The hash value of a git commit.
    tag : :class:`str` or :data:`None`
        The name of a git tag.

    Returns
    -------
    :class:`str` or :data:`None`
        The suffix or :data:`None` if more than 1 of
        `branch`, `tag` or `commit` were enabled.
    """
    count = [bool(branch), bool(commit), bool(tag)].count(True)
    if count == 0:
        return 'main'  # default branch

    if count > 1:
        log.error('Can only specify a branch, a commit or a tag (not multiple options simultaneously)')
        return

    if branch:
        return branch

    if commit:
        return commit

    return tag


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


def _log_install_uninstall_message(packages, action, branch=None, commit=None, tag=None, pkgs_pypi=None):
    """Print the ``install`` or ``uninstall`` summary for what is going to happen.

    Parameters
    ----------
    packages : :class:`dict`
        The packages that are affected.
    action : :class:`str`
        The text to show in color and in upper case about what's happening.
    branch : :class:`str` or :data:`None`
        The name of a git branch to use. Only used when installing packages.
    commit : :class:`str` or :data:`None`
        The hash value of a git commit to use. Only used when installing packages.
    tag : :class:`str` or :data:`None`
        The name of a git tag to use. Only used when installing packages.
    pkgs_pypi : :class:`dict`
        Packages that are on PyPI. Only used when installing packages.
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
            version = '' if (branch or commit or tag) else values['version']
        msg += '\n  {}  {} '.format(name.ljust(w[0]), version.ljust(w[1]))
        if action == 'REMOVED':
            continue
        if branch is not None:
            msg += ' [branch:{}]'.format(branch)
        elif commit is not None:
            msg += ' [commit:{}]'.format(commit[:7])
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
        stream = sys.stdout if record.levelno < logging.WARNING else sys.stderr
        try:
            stream.write(self.COLOURS[record.levelname] + self.format(record) + '\n')
            stream.flush()
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
    if tuple_xy is None or tuple_xy == (0, 0):
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
