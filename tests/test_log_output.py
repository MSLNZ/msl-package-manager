import logging
import os
import sys

import pytest

from msl.package_manager import install
from msl.package_manager import installed
from msl.package_manager import uninstall
from msl.package_manager import update
from msl.package_manager import utils


# see the docs for the caplog fixture
# https://docs.pytest.org/en/latest/logging.html#caplog-fixture
def test_log_output(caplog):
    # checks that the logging messages have the expected output
    caplog.set_level(logging.DEBUG, logger=utils._PKG_NAME)

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
        pass

    # update MSL-LoadLib
    update('loadlib[java]==0.6.0', yes=True)

    # py4j should now be installed

    # update a package that is not an MSL package
    update('colorama', yes=True)

    # uninstall a package that is not an MSL package
    uninstall('colorama', yes=True)

    # install a package that is not part of the msl namespace
    install('GTC<1.3', yes=True, pip_options=['--no-deps'])

    # make sure that GTC is installed
    assert 'GTC' in installed()

    # update GTC -> invalid branch
    update('GTC', yes=True, branch='invalid')

    # update GTC -> invalid tag
    update('GTC', yes=True, tag='invalid')

    # update GTC -> tag=v1.3.1
    update('GTC', yes=True, tag='v1.3.1')

    # uninstall GTC
    uninstall('GTC', yes=True)

    # make sure that GTC is not installed but msl-loadlib is still installed
    assert 'GTC' not in installed()
    assert 'msl-loadlib' in installed()

    # uninstall MSL-LoadLib
    uninstall('loadlib', yes=True)

    # make sure that MSL-LoadLib is not installed
    assert 'msl-loadlib' not in installed()

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
        "The {}'msl-loadlib' package is already installed -- use the update command".format(u),
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
        '\x1b[39mNo packages to update\x1b[39m',

        # msl uninstall colorama -> not an MSL package
        'Getting the packages from {}'.format(exec_path),
        "No MSL packages match 'colorama'",
        'No MSL packages to uninstall',

        # install GTC
        'Loaded the cached information about the PyPI packages',
        'Loaded the cached information about the GitHub repositories',
        'Getting the packages from {}'.format(exec_path),
        '\n\x1b[39mThe following MSL packages will be \x1b[36mINSTALLED\x1b[39m:\n\n  GTC  <1.3  [PyPI]',
        '',
        "Installing {}'GTC' from PyPI".format(u),

        # check if GTC is installed
        'Getting the packages from {}'.format(exec_path),

        # update GTC -> invalid branch
        'Loaded the cached information about the PyPI packages',
        'Loaded the cached information about the GitHub repositories',
        'Getting the packages from {}'.format(exec_path),
        "Cannot update {}'GTC' -- the 'invalid' branch does not exist".format(u),
        '\x1b[39mNo packages to update\x1b[39m',

        # update GTC -> invalid tag
        'Loaded the cached information about the PyPI packages',
        'Loaded the cached information about the GitHub repositories',
        'Getting the packages from {}'.format(exec_path),
        "Cannot update {}'GTC' -- the 'invalid' tag does not exist".format(u),
        '\x1b[39mNo packages to update\x1b[39m',

        # update GTC -> tag=v1.3.1
        'Loaded the cached information about the PyPI packages',
        'Loaded the cached information about the GitHub repositories',
        'Getting the packages from {}'.format(exec_path),
        '\n\x1b[39mThe following MSL packages will be \x1b[36mUPDATED\x1b[39m:\n\n  GTC  1.2.1 --> [tag:v1.3.1]  [GitHub]',
        '',
        "Updating {}'GTC' from GitHub[v1.3.1]".format(u),

        # msl uninstall GTC
        'Getting the packages from {}'.format(exec_path),
        '\n\x1b[39mThe following MSL packages will be \x1b[36mREMOVED\x1b[39m:\n\n  GTC  1.3.1 ',
        '',

        # checking that GTC is not installed
        'Getting the packages from {}'.format(exec_path),

        # checking that msl-loadlib is still installed
        'Getting the packages from {}'.format(exec_path),

        # msl uninstall loadlib
        'Getting the packages from {}'.format(exec_path),
        '\n\x1b[39mThe following MSL packages will be \x1b[36mREMOVED\x1b[39m:\n\n  msl-loadlib  0.6.0 ',
        '',

        # check that msl-loadlib is not installed
        'Getting the packages from {}'.format(exec_path),
    ]

    for index, record in enumerate(caplog.records):
        assert expected[index] == record.message


def test_branch_commit_tag(caplog):
    caplog.set_level(logging.DEBUG, logger=utils._PKG_NAME)

    options = [
        (False, True, True),
        (True, False, True),
        (True, True, False),
        (True, True, True),
    ]

    caplog.clear()
    for b, c, t in options:
        install('does-not-matter', branch=b, commit=c, tag=t)
        update('does-not-matter', branch=b, commit=c, tag=t)
    for r in caplog.records:
        assert r.levelname == 'ERROR'
        assert r.message == 'Can only specify a branch, a commit or a tag (not multiple options simultaneously)'

    cached_has_git = bool(utils.has_git)
    utils.has_git = False

    caplog.clear()
    install('does-not-matter', commit='does-not-matter')
    r = caplog.records[0]
    assert r.levelname == 'ERROR'
    assert r.message == 'Cannot install from a commit because git is not installed'

    caplog.clear()
    update('does-not-matter', commit='does-not-matter')
    r = caplog.records[0]
    assert r.levelname == 'ERROR'
    assert r.message == 'Cannot update from a commit because git is not installed'

    utils.has_git = cached_has_git
