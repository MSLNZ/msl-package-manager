"""
Update MSL packages.
"""
import os
import re
import subprocess
import sys

from colorama import Fore
from pkg_resources import parse_version

from . import _PKG_NAME
from . import utils


def update(*names, **kwargs):
    """Update MSL packages.

    MSL packages can be updated from PyPI packages_ (only if a release has been
    uploaded to PyPI) or from GitHub repositories_.

    .. note::
       If the MSL packages_ are available on PyPI then PyPI is used as the default
       URI_ to update the package. If you want to force the update to occur
       from the ``main`` branch of the GitHub `repository <https://github.com/MSLNZ>`_
       then set ``branch='main'``. If the package is not available on PyPI
       then the ``main`` branch is used as the default update URI_.

    .. _repositories: https://github.com/MSLNZ
    .. _packages: https://pypi.org/search/?q=%22Measurement+Standards+Laboratory+of+New+Zealand%22
    .. _URI: https://en.wikipedia.org/wiki/Uniform_Resource_Identifier

    .. versionchanged:: 2.4.0
        Added the `pip_options` keyword argument.

    .. versionchanged:: 2.5.0
        Added the `include_non_msl` and `commit` keyword arguments. The default
        name of a repository branch changed to ``main``.

    Parameters
    ----------
    *names
        The name(s) of the MSL package(s) to update. If not specified then
        update all MSL packages. The ``msl-`` prefix can be omitted (e.g.,
        ``'loadlib'`` is equivalent to ``'msl-loadlib'``). Also accepts
        shell-style wildcards (e.g., ``'pr-*'``).
    **kwargs
        * branch -- :class:`str`
            The name of a git branch to use to update the package(s) to.
        * commit -- :class:`str`
            The hash value of a git commit to use to update a package.
        * tag -- :class:`str`
            The name of a git tag to use to update a package.
        * update_cache -- :class:`bool`
            The information about the MSL packages_ that are available on PyPI and about
            the repositories_ that are available on GitHub are cached to use for subsequent
            calls to this function. After 24 hours the cache is automatically updated. Set
            `update_cache` to be :data:`True` to force the cache to be updated when you call
            this function. Default is :data:`False`.
        * yes -- :class:`bool`
            If :data:`True` then don't ask for confirmation before updating.
            The default is :data:`False` (ask before updating).
        * pip_options -- :class:`list` of :class:`str`
            Optional arguments to pass to the ``pip install --upgrade`` command,
            e.g., ``['--upgrade-strategy', 'eager']``
        * include_non_msl -- :class:`bool`
            If :data:`True` then also update all non-MSL packages.
            The default is :data:`False` (only update the specified
            MSL packages). Warning, enable this option with caution.

        .. important::
           If you specify a `branch`, `commit` or `tag` then the update will be forced.
    """
    # TODO Python 2.7 does not support named arguments after using *args
    #  we can define yes=False, branch=None, ...
    #  in the function signature when we choose to drop support for Python 2.7
    utils._check_kwargs(kwargs, {'yes', 'branch', 'commit', 'tag',
                                 'update_cache', 'pip_options', 'include_non_msl', 'all_msl'})

    yes = kwargs.get('yes', False)
    branch = kwargs.get('branch', None)
    commit = kwargs.get('commit', None)
    tag = kwargs.get('tag', None)
    update_cache = kwargs.get('update_cache', False)
    pip_options = kwargs.get('pip_options', [])
    include_non_msl = kwargs.get('include_non_msl', False)
    # do not include 'all_msl' in docstring, it is only used internally by the CLI
    all_msl = kwargs.get('all_msl', False)

    if commit and not utils.has_git:
        utils.log.error('Cannot update from a commit because git is not installed')
        return

    github_suffix = utils._get_github_url_suffix(branch=branch, commit=commit, tag=tag)
    if github_suffix is None:
        return

    # keep the order of the log messages consistent: pypi -> github -> local
    pkgs_pypi = utils.pypi(update_cache=update_cache)
    pkgs_github = utils.github(update_cache=update_cache)
    pkgs_installed = utils.installed()
    pkgs_non_msl = utils.outdated_pypi_packages(pkgs_installed) if include_non_msl else {}
    if not pkgs_github and not pkgs_pypi and not pkgs_non_msl:
        return

    if not names or all_msl:
        # update all installed MSL packages only if not updating non-MSL packages
        packages = pkgs_installed if (all_msl or not include_non_msl) else {}
    else:
        packages = utils._check_wildcards_and_prefix(names, pkgs_installed)

    w_non_msl = [0, 0]
    if pkgs_non_msl:
        for name, values in pkgs_non_msl.items():
            w_non_msl = [
                max(w_non_msl[0], len(name)),
                max(w_non_msl[1], len(values['installed_version']))
            ]

    w = [0, 0]
    msl_pkgs_to_update = dict()
    for name, values in packages.items():

        err_msg = 'Cannot update {!r} --'.format(name)

        if name not in pkgs_installed:
            utils.log.error('%s the package is not installed', err_msg)
            continue

        installed_version = pkgs_installed[name]['version']

        # use PyPI to update the package (only if the package is available on PyPI)
        using_pypi = name in pkgs_pypi and not (tag or branch or commit)
        repo_name = pkgs_installed[name]['repo_name']

        # an MSL package could have been installed in "editable" mode, i.e., pip install -e .
        # and therefore it might only exist locally until it is pushed to the repository
        repo = pkgs_github.get(repo_name)
        no_repo_err_msg = '{} the {!r} repository does not exist'.format(err_msg, repo_name)

        extras_require = values['extras_require'] if values.get('extras_require') is not None else ''

        if commit is not None:
            if not repo:
                utils.log.error(no_repo_err_msg)
                continue
            # just assume that the commit value is okay
            msl_pkgs_to_update[name] = {
                'installed_version': installed_version,
                'using_pypi': False,
                'extras_require': extras_require,
                'version': '[commit:{}]'.format(commit[:7]),
                'repo_name': repo_name,
            }
        elif tag is not None:
            if not repo:
                utils.log.error(no_repo_err_msg)
                continue
            if tag in repo['tags']:
                msl_pkgs_to_update[name] = {
                    'installed_version': installed_version,
                    'using_pypi': False,
                    'extras_require': extras_require,
                    'version': '[tag:{}]'.format(tag),
                    'repo_name': repo_name,
                }
            else:
                utils.log.error('%s the %r tag does not exist', err_msg, tag)
                continue
        elif branch is not None:
            if not repo:
                utils.log.error(no_repo_err_msg)
                continue
            if branch in repo['branches']:
                msl_pkgs_to_update[name] = {
                    'installed_version': installed_version,
                    'using_pypi': False,
                    'extras_require': extras_require,
                    'version': '[branch:{}]'.format(branch),
                    'repo_name': repo_name,
                }
            else:
                utils.log.error('%s the %r branch does not exist', err_msg, branch)
                continue
        else:
            if using_pypi:
                version = pkgs_pypi[name]['version']
            else:
                if not repo:
                    utils.log.error(no_repo_err_msg)
                    continue
                version = repo['version']

            if not version:
                # a version number must exist on PyPI,
                # so if this occurs it must be for a GitHub repo
                utils.log.error(
                    '%s the GitHub repository does not contain a release '
                    '(specify a branch, commit or tag)',
                    err_msg
                )
                continue
            elif values.get('version_requested'):
                # this elif must come before the parse_version check
                msl_pkgs_to_update[name] = {
                    'installed_version': installed_version,
                    'using_pypi': using_pypi,
                    'extras_require': extras_require,
                    'version': values['version_requested'],
                    'repo_name': repo_name,
                }
            elif '--force-reinstall' in pip_options or \
                    parse_version(version) > parse_version(installed_version):
                msl_pkgs_to_update[name] = {
                    'installed_version': installed_version,
                    'using_pypi': using_pypi,
                    'extras_require': extras_require,
                    'version': version,
                    'repo_name': repo_name,
                }
            else:
                utils.log.warning('The %r package is already the latest [%s]', name, installed_version)
                continue

        w = [max(w[0], len(name+extras_require)), max(w[1], len(installed_version))]

    msl_pkgs_to_update = utils._sort_packages(msl_pkgs_to_update)

    if not msl_pkgs_to_update and not pkgs_non_msl:
        utils.log.info('%sNo packages to update%s', Fore.RESET, Fore.RESET)
        return

    msg = ''
    if msl_pkgs_to_update:
        msg += '\n{}The following MSL packages will be {}UPDATED{}:\n'.format(Fore.RESET, Fore.CYAN, Fore.RESET)
        for pkg, info in msl_pkgs_to_update.items():
            pkg += info['extras_require'] + '  '
            msg += '\n  ' + pkg.ljust(w[0]+2) + info['installed_version'].ljust(w[1]) + \
                   ' --> ' + info['version'].replace('==', '') + \
                   '  [{}]'.format('PyPI' if info['using_pypi'] else 'GitHub')

    if pkgs_non_msl:
        if msg:
            msg += '\n'
        msg += '\n{}The following non-MSL packages will be {}UPDATED{}:\n'.format(Fore.RESET, Fore.CYAN, Fore.RESET)
        for pkg, info in pkgs_non_msl.items():
            msg += '\n    ' + pkg.ljust(w_non_msl[0]+2) + info['installed_version'].ljust(w_non_msl[1]) + \
                   ' --> ' + info['version'] + '  [PyPI]'

    utils.log.info(msg)
    if not (yes or utils._ask_proceed()):
        return

    utils.log.info('')

    # If updating the msl-package-manager then update it last
    updating_msl_package_manager = _PKG_NAME in msl_pkgs_to_update
    if updating_msl_package_manager:
        value = msl_pkgs_to_update.pop(_PKG_NAME)
        msl_pkgs_to_update[_PKG_NAME] = value  # using an OrderedDict so this item will be last

    zip_extn = 'zip' if utils._IS_WINDOWS else 'tar.gz'
    exe = [sys.executable, '-m', 'pip', 'install']

    if '--upgrade' not in pip_options or '-U' not in pip_options:
        pip_options.append('--upgrade')
    if '--quiet' not in pip_options or '-q' not in pip_options:
        pip_options.extend(['--quiet'] * utils._pip_quiet)
    if '--disable-pip-version-check' not in pip_options:
        pip_options.append('--disable-pip-version-check')

    # install MSL packages
    for pkg, info in msl_pkgs_to_update.items():
        if info['using_pypi']:
            utils.log.debug('Updating %r from PyPI', pkg)
            if info['version'] and info['version'][0] not in '<!=>~':
                info['version'] = '==' + info['version']
            package = [pkg + info['extras_require'] + info['version']]
            pip_github_options = []
        else:
            utils.log.debug('Updating %r from GitHub[%s]', pkg, github_suffix)
            if commit or utils.has_git:
                repo = 'git+https://github.com/MSLNZ/{}.git@{}'.format(info['repo_name'], github_suffix)
            else:
                repo = 'https://github.com/MSLNZ/{}/archive/{}.{}'.format(info['repo_name'], github_suffix, zip_extn)
            repo += '#egg={}'.format(pkg)
            pip_github_options = ['--force-reinstall']
            if info['extras_require']:
                repo += info['extras_require']
            else:
                pip_github_options.append('--no-deps')
            package = [repo]

        if utils._IS_WINDOWS and pkg == _PKG_NAME:
            # On Windows, an executable cannot replace itself while it is running. However,
            # an executable can be renamed while it is running. Therefore, we rename msl.exe
            # to msl.exe.old and then a new msl.exe file can be created during the update
            filename = sys.exec_prefix + '/Scripts/msl.exe'
            os.rename(filename, filename + '.old')

        subprocess.call(exe + pip_options + pip_github_options + package)

    # install non-MSL packages
    if pkgs_non_msl:
        packages = []
        for k, v in pkgs_non_msl.items():
            version = v['version']
            if version[0] not in '<!=>~':
                version = ''
            packages.append('{}{}'.format(k, version))
        utils.log.debug('Updating non-MSL packages from PyPI')
        p = subprocess.Popen(exe + pip_options + packages, stderr=subprocess.PIPE)
        _, err = p.communicate()
        if err:
            message = err.decode().rstrip()
            utils.log.error(message)
            pattern = r'requires (\S+), but you have'
            for requires in re.findall(pattern, message):
                utils.log.warning('Rolling back to %r', requires)
                subprocess.call(exe + pip_options + [requires])

    if updating_msl_package_manager:
        return 'updating_msl_package_manager'
