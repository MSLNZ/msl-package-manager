"""
Uninstall MSL packages.
"""
import os
import sys
import subprocess

from . import utils


def uninstall(*names, **kwargs):
    """Uninstall MSL packages.

    Parameters
    ----------
    *names : :class:`str`
        The name(s) of the MSL package(s) to uninstall. If not specified then
        uninstall all MSL packages (except for the **MSL Package Manager** --
        in which case use ``pip uninstall msl-package-manager``). The
        ``msl-`` prefix can be omitted (e.g., ``'loadlib'`` is equivalent to
        ``'msl-loadlib'``). Also accepts shell-style wildcards (e.g., ``'pr-*'``).
    **kwargs
        * yes : :class:`bool`
            If :data:`True` then don't ask for confirmation before uninstalling.
            The default is :data:`False` (ask before uninstalling).
    """
    # Python 2.7 does not support named arguments after using *args
    # we can define yes=False in the function signature
    # if we choose to drop support for Python 2.7
    utils._check_kwargs(kwargs, {'yes', })

    yes = kwargs.get('yes', False)

    packages = utils._create_uninstall_list(names)
    if not packages:
        utils.log.info('No MSL packages to uninstall.')
        return

    # use the word REMOVE since it visibly looks different than UNINSTALL and INSTALL do
    utils._log_install_uninstall_message(packages, 'REMOVED', None, None)
    if not (yes or utils._ask_proceed()):
        return

    # After a MSL package gets uninstalled the "msl" namespace gets destroyed.
    # This is a known issue:
    #   https://github.com/pypa/sample-namespace-packages/issues/5
    #   https://github.com/pypa/python-packaging-user-guide/issues/314
    # There are few ways to bypass this issue
    #   1. force all MSL packages to require that the MSL Package Manager is installed
    #      and only the MSL Package Manager contains the namespace __init__.py file
    #   2. modify the setup.py of each namespace package to have "packages=" include
    #      only the child package.
    #   3. what is done below... assume that MSL packages are uninstalled using the
    #      MSL Package Manager and then re-create the __init__.py files after a
    #      package is uninstalled.

    template_dir = os.path.join(os.path.dirname(__file__), 'template', 'msl')
    with open(os.path.join(template_dir, '__init__.py.template'), 'r') as fp:
        msl_init = fp.readlines()
    with open(os.path.join(template_dir, 'examples', '__init__.py.template'), 'r') as fp:
        msl_examples_init = fp.readlines()

    utils.log.info('')

    exe = [sys.executable, '-m', 'pip', 'uninstall']
    options = ['--disable-pip-version-check', '--yes'] + ['--quiet'] * utils._NUM_QUIET
    for pkg in packages:
        subprocess.call(exe + options + [pkg])
        if pkg.startswith('msl-'):
            with open(os.path.join(os.path.dirname(__file__), '..', '__init__.py'), 'w') as fp:
                fp.writelines(msl_init)
            with open(os.path.join(os.path.dirname(__file__), '..', 'examples', '__init__.py'), 'w') as fp:
                fp.writelines(msl_examples_init)
