"""
Install MSL packages.
"""
import sys
import subprocess

from . import utils


def install(*names, **kwargs):
    """Install MSL packages.

    MSL packages can be installed from PyPI packages_ (only if a release has been
    uploaded to PyPI_) or from GitHub repositories_.

    .. note::
       If the MSL packages_ are available on PyPI_ then PyPI_ is used as the default
       URI_ to install the package. If you want to force the installation to occur
       from the ``master`` branch of the GitHub `repository <https://github.com/MSLNZ>`_
       then set ``branch='master'``. If the package is not available on PyPI_
       then the ``master`` branch is used as the default installation URI_.

    .. _repositories: https://github.com/MSLNZ
    .. _packages: https://pypi.org/search/?q=msl-
    .. _PyPI: https://pypi.org/
    .. _URI: https://en.wikipedia.org/wiki/Uniform_Resource_Identifier

    Parameters
    ----------
    *names : :class:`tuple` of :class:`str`, optional
        The name(s) of the MSL package(s) to install. If empty then
        install **all** MSL packages.
    **kwargs
        yes : :class:`bool`, default :data:`False`
            If :data:`True` then don't ask for confirmation before installing.
            The default is to ask before installing.
        branch : :class:`str`, default :data:`None`
            The name of a GitHub branch to use for the installation. If :data:`None`,
            and no `tag` value has been specified, then installs from the ``master``
            branch.
        tag : :class:`str`, default :data:`None`
            The name of a GitHub tag to use for the installation.
        update_cache : :class:`bool`, default :data:`False`
            The information about the MSL packages_ that are available on PyPI_ and about
            the repositories_ that are available on GitHub are cached to use for subsequent
            calls to this function. After 24 hours the cache is automatically updated. Set
            `update_cache` to be :data:`True` to force the cache to be updated when you call
            this function.

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
        utils.log.info('No MSL packages to install')
        return

    pkgs_pypi = utils.pypi(update_cache)

    utils._log_install_uninstall_message(packages, 'INSTALLED', branch, tag)
    if not (yes or utils._ask_proceed()):
        return

    utils.log.info('')

    exe = [sys.executable, '-m', 'pip', 'install']
    options = ['--quiet'] * utils._NUM_QUIET
    github_options = ['--process-dependency-links']
    for pkg in packages:
        if pkg in pkgs_pypi and branch is None and tag is None:
            utils.log.debug('Installing {} from PyPI'.format(pkg))
            subprocess.call(exe + options + [pkg])
        else:
            utils.log.debug('Installing {} from GitHub/{}'.format(pkg, zip_name))
            repo = ['https://github.com/MSLNZ/{}/archive/{}.zip'.format(pkg, zip_name)]
            subprocess.call(exe + options + github_options + repo)
