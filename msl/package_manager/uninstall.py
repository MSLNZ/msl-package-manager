"""
Uninstall MSL packages.
"""
import os
import sys
import subprocess
import pkg_resources

from . import utils


def uninstall(*names, **kwargs):
    """Uninstall MSL packages.

    Parameters
    ----------
    *names
        The name(s) of the MSL package(s) to uninstall. If not specified then
        uninstall all MSL packages (except for the **MSL Package Manager** --
        in which case use ``pip uninstall msl-package-manager``). The
        ``msl-`` prefix can be omitted (e.g., ``'loadlib'`` is equivalent to
        ``'msl-loadlib'``). Also accepts shell-style wildcards (e.g., ``'pr-*'``).
    **kwargs
        * yes : :class:`bool`
            If :data:`True` then don't ask for confirmation before uninstalling.
            The default is :data:`False` (ask before uninstalling).
        * pip_options : :class:`list` of :class:`str`
            Optional arguments to pass to the ``pip uninstall`` command,
            e.g., ``['--no-python-version-warning']``

    """
    # TODO Python 2.7 does not support named arguments after using *args
    #  we can define yes=False, pip_options=None in the function signature
    #  when we choose to drop support for Python 2.7
    utils._check_kwargs(kwargs, {'yes', 'pip_options'})

    yes = kwargs.get('yes', False)
    pip_options = kwargs.get('pip_options', [])

    packages = utils._create_uninstall_list(names)
    if not packages:
        utils.log.info('No MSL packages to uninstall')
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

    def check_if_namespace_package(package_name):
        for dist in pkg_resources.working_set:
            if dist.project_name in package_name:
                split = package_name.split('-')
                if len(split) != 2:
                    break

                examples_init_file = os.path.join(dist.module_path, split[0], 'examples', '__init__.py')
                if not os.path.isfile(examples_init_file):
                    break

                with open(examples_init_file, 'rt') as fp:
                    examples_init = fp.readlines()

                init_file = os.path.join(dist.module_path, split[0], '__init__.py')
                if not os.path.isfile(init_file):
                    break

                with open(init_file, 'rt') as fp:
                    init = fp.readlines()

                for line in init:
                    if '__path__' in line and 'pkgutil' in line:
                        return True, os.path.dirname(init_file), init, examples_init

        return False, None, None, None

    utils.log.info('')

    exe = [sys.executable, '-m', 'pip', 'uninstall']

    if '--quiet' not in pip_options or '-q' not in pip_options:
        pip_options.extend(['--quiet'] * utils._NUM_QUIET)
    if '--disable-pip-version-check' not in pip_options:
        pip_options.append('--disable-pip-version-check')
    if '--yes' not in pip_options or '-y' not in pip_options:
        pip_options.append('--yes')

    for pkg in packages:
        is_namespace, path, init, examples_init = check_if_namespace_package(pkg)
        subprocess.call(exe + pip_options + [pkg])
        if is_namespace and os.path.isdir(path):
            with open(os.path.join(path, '__init__.py'), 'wt') as fp:
                fp.writelines(init)
            with open(os.path.join(path, 'examples', '__init__.py'), 'wt') as fp:
                fp.writelines(examples_init)
