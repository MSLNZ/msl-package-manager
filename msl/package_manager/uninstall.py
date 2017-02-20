"""
Use pip to uninstall MSL packages.
"""
import subprocess

from .helper import _get_packages


def uninstall(names='ALL', yes=False):
    """
    Use pip to uninstall MSL packages.

    Args:
        names (str, list[str], optional): The name of a single MSL package or a list
            of MSL package names to uninstall. Default is to uninstall all MSL packages
            (except for the **msl-package-manager**).

        yes (bool, optional): Don't ask for confirmation to uninstall. Default is
            to ask before uninstalling.
    """
    for pkg in _get_packages('uninstall', names, yes):
        subprocess.call(['pip', 'uninstall', '-y', pkg])
