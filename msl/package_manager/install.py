"""
Install MSL packages.
"""
import sys
import subprocess

from . import utils


def install(*names, **kwargs):
    """Install MSL packages.

    MSL packages can be installed from PyPI packages_ (only if a release has been
    uploaded to PyPI) or from GitHub repositories_.

    .. note::
       If the MSL packages_ are available on PyPI then PyPI is used as the default
       URI_ to install the package. If you want to force the installation to occur
       from the ``master`` branch of the GitHub `repository <https://github.com/MSLNZ>`_
       then set ``branch='master'``. If the package is not available on PyPI
       then the ``master`` branch is used as the default installation URI_.

    .. _repositories: https://github.com/MSLNZ
    .. _packages: https://pypi.org/search/?q=msl-
    .. _URI: https://en.wikipedia.org/wiki/Uniform_Resource_Identifier

    Parameters
    ----------
    *names : :class:`str`
        The name(s) of the MSL package(s) to install. If not specified then
        install all MSL packages that begin with the ``msl-`` prefix. The
        ``msl-`` prefix can be omitted (e.g., ``'loadlib'`` is equivalent to
        ``'msl-loadlib'``). Also accepts shell-style wildcards (e.g., ``'pr-*'``).
    **kwargs
        * yes : :class:`bool`
            If :data:`True` then don't ask for confirmation before installing.
            The default is :data:`False` (ask before installing).
        * branch : :class:`str`
            The name of a GitHub branch to use for the installation. If :data:`None`,
            and no `tag` value has been specified, then installs from the ``master``
            branch. Default is :data:`None`.
        * tag : :class:`str`
            The name of a GitHub tag to use for the installation. Default is :data:`None`.
        * update_cache : :class:`bool`
            The information about the MSL packages_ that are available on PyPI and about
            the repositories_ that are available on GitHub are cached to use for subsequent
            calls to this function. After 24 hours the cache is automatically updated. Set
            `update_cache` to be :data:`True` to force the cache to be updated when you call
            this function. Default is :data:`False`.

        .. attention::
           Cannot specify both a `branch` and a `tag` simultaneously.
    """
    # Python 2.7 does not support named arguments after using *args
    # we can define yes=False, branch=None, tag=None, update_cache=False in the function signature
    # if we choose to drop support for Python 2.7
    utils._check_kwargs(kwargs, {'yes', 'branch', 'tag', 'update_cache'})

    yes = kwargs.get('yes', False)
    branch = kwargs.get('branch', None)
    tag = kwargs.get('tag', None)
    update_cache = kwargs.get('update_cache', False)

    zip_name = utils._get_github_zip_name(branch, tag)
    if zip_name is None:
        return

    packages = utils._create_install_list(names, branch, tag, update_cache)
    if not packages:
        utils.log.info('No MSL packages to install.')
        return

    pkgs_pypi = utils.pypi(update_cache)

    utils._log_install_uninstall_message(packages, 'INSTALLED', branch, tag)
    if not (yes or utils._ask_proceed()):
        return

    utils.log.info('')

    zip_extn = 'zip' if utils._IS_WINDOWS else 'tar.gz'
    exe = [sys.executable, '-m', 'pip', 'install']
    options = ['--disable-pip-version-check'] + ['--quiet'] * utils._NUM_QUIET
    for pkg in packages:
        if pkg in pkgs_pypi and branch is None and tag is None:
            utils.log.debug('Installing {!r} from PyPI'.format(pkg))
            subprocess.call(exe + options + [pkg])
        else:
            utils.log.debug('Installing {!r} from GitHub/{}'.format(pkg, zip_name))
            repo = 'https://github.com/MSLNZ/{}/archive/{}.{}'.format(pkg, zip_name, zip_extn)
            subprocess.call(exe + options + [repo])
