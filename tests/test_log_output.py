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
    install('loadlib==0.5.0', yes=True)

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

    #
    # the expected logging messages
    #
    exec_path = os.path.dirname(sys.executable)
    loadlib_name = "u'msl-loadlib'" if sys.version_info.major == 2 else "'msl-loadlib'"
    expected = [
        # msl install loadlib==0.5.0
        'Getting the packages from {}'.format(exec_path),
        'Loaded the cached information about the GitHub repositories',
        'Loaded the cached information about the PyPI packages',
        '\n\x1b[39mThe following MSL packages will be \x1b[36mINSTALLED\x1b[39m:\n\n  msl-loadlib  0.5.0    [PyPI]',
        '',
        'Installing {} from PyPI'.format(loadlib_name),

        # check if msl-loadlib is installed
        'Getting the packages from {}'.format(exec_path),

        # msl install does_not_exist -> a that package does not exist
        'Getting the packages from {}'.format(exec_path),
        'Loaded the cached information about the GitHub repositories',
        'No MSL packages match \'does_not_exist\'',
        'No MSL packages to install.',

        # msl install loadlib -> already installed
        'Getting the packages from {}'.format(exec_path),
        'Loaded the cached information about the GitHub repositories',
        'The {} package is already installed.'.format(loadlib_name),
        'No MSL packages to install.',

        # msl update loadlib[java]==0.6.0
        'Getting the packages from {}'.format(exec_path),
        'Loaded the cached information about the GitHub repositories',
        'Loaded the cached information about the PyPI packages',
        '\n\x1b[39mThe following MSL packages will be \x1b[36mUPDATED\x1b[39m:\n\n  msl-loadlib[java]: 0.5.0 --> 0.6.0  [PyPI]',
        '',
        'Updating {} from PyPI'.format(loadlib_name),

        # msl update colorama -> not an MSL package
        'Getting the packages from {}'.format(exec_path),
        'Loaded the cached information about the GitHub repositories',
        'Loaded the cached information about the PyPI packages',
        'No MSL packages match \'colorama\'',
        '\x1b[39mNo MSL packages to update.\x1b[39m',

        # msl uninstall colorama -> not an MSL package
        'Getting the packages from {}'.format(exec_path),
        'No MSL packages match \'colorama\'',
        'No MSL packages to uninstall.',

        # msl uninstall loadlib
        'Getting the packages from {}'.format(exec_path),
        '\n\x1b[39mThe following MSL packages will be \x1b[36mREMOVED\x1b[39m:\n\n  msl-loadlib  0.6.0 ',
        '',

        # check if msl-loadlib is installed
        'Getting the packages from {}'.format(exec_path),
    ]

    for index, record in enumerate(caplog.records):
        assert expected[index] == record.message
