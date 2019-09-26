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

    if sys.version_info[:2] >= (3, 5):
        # rpi-smartgadget requires msl-network which require Python 3.5+

        # msl install rpi-smartgadget
        install('rpi-smartgadget', yes=True)

        # make sure that smartgadget and msl-network are installed
        installed_ = installed()
        assert 'smartgadget' in installed_
        assert 'msl-network' in installed_

        # update rpi-smartgadget -> invalid branch
        update('smartgadget', yes=True, branch='invalid')

        # update rpi-smartgadget -> invalid tag
        update('smartgadget', yes=True, tag='invalid')

        # update rpi-smartgadget
        update('smartgadget', yes=True, branch='master')

        # uninstall rpi-smartgadget
        uninstall('smartgadget', 'network', yes=True)

        # make sure that smartgadget and msl-network are not installed
        installed_ = installed()
        assert 'smartgadget' not in installed_
        assert 'msl-network' not in installed_

    #
    # the expected logging messages
    #
    exec_path = os.path.dirname(sys.executable)
    u = 'u' if sys.version_info.major == 2 else ''
    expected = [
        # msl install loadlib==0.5.0
        'Loaded the cached information about the PyPI packages',
        'Loaded the cached information about the GitHub repositories',
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
        '\n\x1b[39mThe following MSL packages will be \x1b[36mUPDATED\x1b[39m:\n\n  msl-loadlib[java]: 0.5.0 --> 0.6.0  [PyPI]',
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
    ]

    if sys.version_info[:2] >= (3, 5):
        expected.extend([
            # install rpi-smartgadget
            'Loaded the cached information about the PyPI packages',
            'Loaded the cached information about the GitHub repositories',
            'Getting the packages from {}'.format(exec_path),
            '\n\x1b[39mThe following MSL packages will be \x1b[36mINSTALLED\x1b[39m:\n\n  rpi-smartgadget    [GitHub]',
            '',
            "Installing {}'rpi-smartgadget' from GitHub/master".format(u),

            # check if smartgadget and msl-network are installed
            'Getting the packages from {}'.format(exec_path),

            # update rpi-smartgadget -> invalid branch
            'Loaded the cached information about the PyPI packages',
            'Loaded the cached information about the GitHub repositories',
            'Getting the packages from {}'.format(exec_path),
            "Cannot update 'smartgadget' -- The 'invalid' branch does not exist",
            '\x1b[39mNo MSL packages to update\x1b[39m',

            # update rpi-smartgadget -> invalid tag
            'Loaded the cached information about the PyPI packages',
            'Loaded the cached information about the GitHub repositories',
            'Getting the packages from {}'.format(exec_path),
            "Cannot update 'smartgadget' -- The 'invalid' tag does not exist",
            '\x1b[39mNo MSL packages to update\x1b[39m',

            # update rpi-smartgadget -> master branch
            'Loaded the cached information about the PyPI packages',
            'Loaded the cached information about the GitHub repositories',
            'Getting the packages from {}'.format(exec_path),
            '\n\x1b[39mThe following MSL packages will be \x1b[36mUPDATED\x1b[39m:\n\n  smartgadget: 0.1.0.dev0 --> [branch:master]  [GitHub]',
            '',
            "Updating {}'smartgadget' from GitHub/master".format(u),

            # msl uninstall smartgadget network
            'Getting the packages from {}'.format(exec_path),
            '\n\x1b[39mThe following MSL packages will be \x1b[36mREMOVED\x1b[39m:\n\n  msl-network  0.4.1      \n  smartgadget  0.1.0.dev0 ',
            '',

            # checking that smartgadget and msl-network are not installed
            'Getting the packages from {}'.format(exec_path),
    ])

    for index, record in enumerate(caplog.records):
        assert expected[index] == record.message
