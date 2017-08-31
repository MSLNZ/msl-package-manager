"""
Use pip to uninstall MSL packages.
"""
import os
import sys
import subprocess

from .helper import _get_packages


def uninstall(names='ALL', yes=False):
    """Use pip to uninstall MSL packages.

    Parameters
    ----------
    names : :obj:`str` or :obj:`list` of :obj:`str`, optional
        The name(s) of MSL package(s) to uninstall. Default is to uninstall **all** MSL
        packages (except for the **MSL Package Manager**).
    yes : :obj:`bool`, optional
        Don't ask for confirmation to uninstall. Default is to ask before uninstalling.
    """

    # after a MSL package gets uninstalled we must re-create the two "__init__.py"
    # package files to maintain the 'msl' namespace
    template_dir = os.path.join(os.path.dirname(__file__), 'template', 'msl')
    with open(os.path.join(template_dir, '__init__.py.template'), 'r') as fp:
        msl_init = fp.readlines()
    with open(os.path.join(template_dir, 'examples', '__init__.py.template'), 'r') as fp:
        msl_examples_init = fp.readlines()

    for pkg in _get_packages('uninstall', names, yes):
        subprocess.call([sys.executable, '-m', 'pip', 'uninstall', '-y', pkg])

        with open(os.path.join(os.path.dirname(__file__), '..', '__init__.py'), 'w') as fp:
            fp.writelines(msl_init)
        with open(os.path.join(os.path.dirname(__file__), '..', 'examples', '__init__.py'), 'w') as fp:
            fp.writelines(msl_examples_init)
