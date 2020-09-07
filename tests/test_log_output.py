import os
import sys
import logging

import pytest

from msl.package_manager import install, update, uninstall, installed, _PKG_NAME


# see the docs for the caplog fixture
# https://docs.pytest.org/en/latest/logging.html#caplog-fixture
def test_log_output(caplog):
    # checks that the logging messages have the expected output
    caplog.set_level(logging.DEBUG, logger=_PKG_NAME)

    # install MSL-LoadLib version 0.5.0
    install('loadlib==0.5.0', yes=True, update_cache=True)

    # make sure that MSL-LoadLib is installed
    assert 'msl-loadlib' in installed()

    # install a package that does not exist
    install('does_not_exist', yes=True)

    # install MSL-LoadLib
    install('loadlib', yes=True)

    # check that py4j is not installed
    with pytest.raises(ImportError):
        import py4j

    # update MSL-LoadLib
    update('loadlib[java]==0.6.0', yes=True)

    # py4j should now be installed
    import py4j

    # update a package that is not an MSL package
    update('colorama', yes=True)

    # uninstall a package that is not an MSL package
    uninstall('colorama', yes=True)
    import colorama  # still installed

    # uninstall MSL-LoadLib
    uninstall('loadlib', yes=True)

    # make sure that MSL-LoadLib is not installed
    assert 'msl-loadlib' not in installed()

    # install a package that is not part of the msl namespace
    install('Quantity-Value<0.2', yes=True)

    # make sure that Quantity-Value is installed
    assert 'Quantity-Value' in installed()

    # update Quantity-Value -> invalid branch
    update('Quantity-Value', yes=True, branch='invalid')

    # update Quantity-Value -> invalid tag
    update('Quantity-Value', yes=True, tag='invalid')

    # update Quantity-Value -> tag=v0.1.0
    update('Quantity-Value', yes=True, tag='v0.1.0')

    # uninstall Quantity-Value
    uninstall('Quantity-Value', yes=True)

    # make sure that Quantity-Value is not installed
    assert 'Quantity-Value' not in installed()

    #
    # the expected logging messages
    #
    exec_path = os.path.dirname(sys.executable)
    u = 'u' if sys.version_info.major == 2 else ''
    expected = [
        # msl install loadlib==0.5.0
        'Getting the packages from PyPI',
        'Getting the repositories from GitHub',
        'Getting the packages from {}'.format(exec_path),
        '\n\x1b[39mThe following MSL packages will be \x1b[36mINSTALLED\x1b[39m:\n\n  msl-loadlib  0.5.0    [PyPI]',
        '',
        "Installing {}'msl-loadlib' from PyPI".format(u),

        # check if msl-loadlib is installed
        'Getting the packages from {}'.format(exec_path),

        # msl install does_not_exist -> a that package does not exist
        'Loaded the cached information about the PyPI packages',
        'Loaded the cached information about the GitHub repositories',
        'Getting the packages from {}'.format(exec_path),
        "No MSL packages match 'does_not_exist'",
        'No MSL packages to install',

        # msl install loadlib -> already installed
        'Loaded the cached information about the PyPI packages',
        'Loaded the cached information about the GitHub repositories',
        'Getting the packages from {}'.format(exec_path),
        "The {}'msl-loadlib' package is already installed".format(u),
        'No MSL packages to install',

        # msl update loadlib[java]==0.6.0
        'Loaded the cached information about the PyPI packages',
        'Loaded the cached information about the GitHub repositories',
        'Getting the packages from {}'.format(exec_path),
        '\n\x1b[39mThe following MSL packages will be \x1b[36mUPDATED\x1b[39m:\n\n  msl-loadlib[java]  0.5.0 --> 0.6.0  [PyPI]',
        '',
        "Updating {}'msl-loadlib' from PyPI".format(u),

        # msl update colorama -> not an MSL package
        'Loaded the cached information about the PyPI packages',
        'Loaded the cached information about the GitHub repositories',
        'Getting the packages from {}'.format(exec_path),
        "No MSL packages match 'colorama'",
        '\x1b[39mNo MSL packages to update\x1b[39m',

        # msl uninstall colorama -> not an MSL package
        'Getting the packages from {}'.format(exec_path),
        "No MSL packages match 'colorama'",
        'No MSL packages to uninstall',

        # msl uninstall loadlib
        'Getting the packages from {}'.format(exec_path),
        '\n\x1b[39mThe following MSL packages will be \x1b[36mREMOVED\x1b[39m:\n\n  msl-loadlib  0.6.0 ',
        '',

        # check if msl-loadlib is installed
        'Getting the packages from {}'.format(exec_path),

        # install Quantity-Value
        'Loaded the cached information about the PyPI packages',
        'Loaded the cached information about the GitHub repositories',
        'Getting the packages from {}'.format(exec_path),
        '\n\x1b[39mThe following MSL packages will be \x1b[36mINSTALLED\x1b[39m:\n\n  Quantity-Value  <0.2  [PyPI]',
        '',
        "Installing {}'Quantity-Value' from PyPI".format(u),

        # check if Quantity-Value is installed
        'Getting the packages from {}'.format(exec_path),

        # update Quantity-Value -> invalid branch
        'Loaded the cached information about the PyPI packages',
        'Loaded the cached information about the GitHub repositories',
        'Getting the packages from {}'.format(exec_path),
        "Cannot update {}'Quantity-Value' -- The 'invalid' branch does not exist".format(u),
        '\x1b[39mNo MSL packages to update\x1b[39m',

        # update Quantity-Value -> invalid tag
        'Loaded the cached information about the PyPI packages',
        'Loaded the cached information about the GitHub repositories',
        'Getting the packages from {}'.format(exec_path),
        "Cannot update {}'Quantity-Value' -- The 'invalid' tag does not exist".format(u),
        '\x1b[39mNo MSL packages to update\x1b[39m',

        # update Quantity-Value -> tag=v0.1.0
        'Loaded the cached information about the PyPI packages',
        'Loaded the cached information about the GitHub repositories',
        'Getting the packages from {}'.format(exec_path),
        '\n\x1b[39mThe following MSL packages will be \x1b[36mUPDATED\x1b[39m:\n\n  Quantity-Value  0.1.0 --> [tag:v0.1.0]  [GitHub]',
        '',
        "Updating {}'Quantity-Value' from GitHub[v0.1.0]".format(u),

        # msl uninstall Quantity-Value
        'Getting the packages from {}'.format(exec_path),
        '\n\x1b[39mThe following MSL packages will be \x1b[36mREMOVED\x1b[39m:\n\n  Quantity-Value  0.1.0 ',
        '',

        # checking that Quantity-Value is not installed
        'Getting the packages from {}'.format(exec_path),
    ]

    for index, record in enumerate(caplog.records):
        assert expected[index] == record.message
