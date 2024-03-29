"""
Install MSL packages.
"""
import subprocess
import sys

from . import utils

# Fixes issue #8 (repository name != package name)
# Not sure how to generalize a universal solution since one is free to choose
# any repository name and package name, therefore this mapping will need to be
# updated on a case-by-case basis in future releases of msl-package-manager
#
# key: repo name, value: package (egg) name
_egg_name_map = {
    'pr-omega-logger': 'omega-logger',
    'pr-single-photons': 'photons',
    'pr-superk-mono': 'superk-mono',
    'pr-webpage-text': 'webpage-text',
    'rpi-ocr': 'ocr',
    'rpi-smartgadget': 'smartgadget',
}


def install(*names, **kwargs):
    """Install MSL packages.

    MSL packages can be installed from PyPI packages_ (only if a release has been
    uploaded to PyPI) or from GitHub repositories_.

    .. note::
       If the MSL packages_ are available on PyPI then PyPI is used as the default
       location to install the package. If you want to force the installation to occur
       from the ``main`` branch from GitHub (even though the package is available on PyPI)
       then set ``branch='main'``. If the package is not available on PyPI
       then the ``main`` branch is used as the default installation location.

    .. _repositories: https://github.com/MSLNZ
    .. _packages: https://pypi.org/search/?q=%22Measurement+Standards+Laboratory+of+New+Zealand%22

    .. versionchanged:: 2.4.0
        Added the `pip_options` keyword argument.

    .. versionchanged:: 2.5.0
        Added the `commit` keyword argument. The default name of a
        repository branch changed to ``main``.

    Parameters
    ----------
    *names
        The name(s) of the MSL package(s) to install. If not specified then
        install all MSL packages that begin with the ``msl-`` prefix. The
        ``msl-`` prefix can be omitted (e.g., ``'loadlib'`` is equivalent to
        ``'msl-loadlib'``). Also accepts shell-style wildcards (e.g., ``'pr-*'``).
    **kwargs
        * branch -- :class:`str`
            The name of a git branch to install. If not specified and neither a
            `tag` nor `commit` was specified then the ``main`` branch is used to
            install a package if it is not available on PyPI.
        * commit -- :class:`str`
            The hash value of a git commit to use to install a package.
        * tag -- :class:`str`
            The name of a git tag to use to install a package.
        * update_cache -- :class:`bool`
            The information about the MSL packages_ that are available on PyPI and about
            the repositories_ that are available on GitHub are cached to use for subsequent
            calls to this function. After 24 hours the cache is automatically updated. Set
            `update_cache` to be :data:`True` to force the cache to be updated when you call
            this function. Default is :data:`False`.
        * yes -- :class:`bool`
            If :data:`True` then don't ask for confirmation before installing.
            The default is :data:`False` (ask before installing).
        * pip_options -- :class:`list` of :class:`str`
            Optional arguments to pass to the ``pip install`` command,
            e.g., ``['--retries', '10', '--user']``

    """
    # TODO Python 2.7 does not support named arguments after using *args
    #  we can define yes=False, branch=None, ...
    #  in the function signature when we choose to drop support for Python 2.7
    utils._check_kwargs(kwargs, {'yes', 'branch', 'commit', 'tag', 'update_cache', 'pip_options'})

    yes = kwargs.get('yes', False)
    branch = kwargs.get('branch', None)
    commit = kwargs.get('commit', None)
    tag = kwargs.get('tag', None)
    update_cache = kwargs.get('update_cache', False)
    pip_options = kwargs.get('pip_options', [])

    if commit and not utils.has_git:
        utils.log.error('Cannot install from a commit because git is not installed')
        return

    github_suffix = utils._get_github_url_suffix(branch=branch, commit=commit, tag=tag)
    if github_suffix is None:
        return

    # keep the order of the log messages consistent: pypi -> github -> local
    # utils._create_install_list() does github -> local
    pkgs_pypi = utils.pypi(update_cache)
    packages = utils._create_install_list(names, branch, commit, tag, update_cache)
    if not packages:
        utils.log.info('No MSL packages to install')
        return

    utils._log_install_uninstall_message(
        packages, 'INSTALLED', branch=branch, commit=commit, tag=tag, pkgs_pypi=pkgs_pypi
    )
    if not (yes or utils._ask_proceed()):
        return

    utils.log.info('')

    zip_extn = 'zip' if utils._IS_WINDOWS else 'tar.gz'
    exe = [sys.executable, '-m', 'pip', 'install']

    if '--quiet' not in pip_options or '-q' not in pip_options:
        pip_options.extend(['--quiet'] * utils._pip_quiet)
    if '--disable-pip-version-check' not in pip_options:
        pip_options.append('--disable-pip-version-check')

    for name, values in packages.items():
        if name in pkgs_pypi and not (branch or commit or tag):
            utils.log.debug('Installing %r from PyPI', name)
            if values['extras_require']:
                name += values['extras_require']
            if values['version_requested']:
                name += values['version_requested']
            subprocess.call(exe + pip_options + [name])
        else:
            utils.log.debug('Installing %r from GitHub[%s]', name, github_suffix)
            if commit or utils.has_git:
                repo = 'git+https://github.com/MSLNZ/{}.git@{}'.format(name, github_suffix)
            else:
                repo = 'https://github.com/MSLNZ/{}/archive/{}.{}'.format(name, github_suffix, zip_extn)

            egg_name = _egg_name_map.get(name, name)
            repo += '#egg={}'.format(egg_name)
            if values['extras_require']:
                repo += values['extras_require']
            subprocess.call(exe + pip_options + [repo])
