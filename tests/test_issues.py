import json
import sys

import colorama
import pytest

from msl.package_manager import install
from msl.package_manager import installed
from msl.package_manager import uninstall
from msl.package_manager import update
from msl.package_manager import utils


@pytest.mark.skipif(sys.version_info[:2] < (3, 6), reason='only test in Python 3.6+')
def test_issue8_a():
    repo = 'pr-omega-logger'
    pkg = 'omega-logger'
    assert pkg not in installed()
    install(repo, yes=True)
    assert pkg in installed()
    update(pkg, branch='main', yes=True)
    assert pkg in installed()

    # msl-equipment, msl-io and msl-loadlib are also installed
    # do not include any packages in the call to uninstall() to
    # uninstall all MSL packages that were installed in this test
    uninstall(yes=True)
    installed_ = installed()
    assert pkg not in installed_
    assert 'msl-equipment' not in installed_
    assert 'msl-loadlib' not in installed_
    assert 'msl-io' not in installed_


@pytest.mark.skipif(sys.version_info[:2] != (2, 7), reason='only test in Python 2.7')
def test_issue8_b():
    # test issue 8 in Python 2.7 since pr-omega-logger requires Python 3.6+
    repo = 'pr-webpage-text'
    pkg = 'webpage-text'
    assert pkg not in installed()
    install(repo, yes=True)
    assert pkg in installed()
    update(pkg, branch='main', yes=True)
    assert pkg in installed()
    uninstall(pkg, yes=True)
    assert pkg not in installed()


def test_issue_11(caplog):
    # installed packages
    utils.info(as_json=True)
    assert len(caplog.messages) == 3
    record = caplog.records[0]
    assert record.levelname == 'DEBUG'
    assert record.message.startswith('Getting the packages from ')
    record = caplog.records[1]
    assert record.levelname == 'DEBUG'
    assert record.message == colorama.Fore.RESET
    record = caplog.records[2]
    assert record.levelname == 'INFO'
    pkgs = json.loads(record.message)
    requires = sorted(pkgs[utils._PKG_NAME]['requires'])
    assert requires == ['colorama', 'setuptools']

    caplog.clear()

    # from PyPI
    utils.info(as_json=True, from_pypi=True)
    assert len(caplog.messages) == 3
    record = caplog.records[0]
    assert record.levelname == 'DEBUG'
    assert record.message == 'Loaded the cached information about the PyPI packages'
    record = caplog.records[1]
    assert record.levelname == 'DEBUG'
    assert record.message == colorama.Fore.RESET
    record = caplog.records[2]
    assert record.levelname == 'INFO'
    pkgs = json.loads(record.message)
    assert utils._PKG_NAME in pkgs
    assert 'requires' not in pkgs[utils._PKG_NAME]
    assert 'version' in pkgs[utils._PKG_NAME]
    assert 'description' in pkgs[utils._PKG_NAME]

    caplog.clear()

    # from GitHub
    utils.info(as_json=True, from_github=True)
    assert len(caplog.messages) == 3
    record = caplog.records[0]
    assert record.levelname == 'DEBUG'
    assert record.message == 'Loaded the cached information about the GitHub repositories'
    record = caplog.records[1]
    assert record.levelname == 'DEBUG'
    assert record.message == colorama.Fore.RESET
    record = caplog.records[2]
    assert record.levelname == 'INFO'
    pkgs = json.loads(record.message)
    assert utils._PKG_NAME in pkgs
    assert 'requires' not in pkgs[utils._PKG_NAME]
    assert 'version' in pkgs[utils._PKG_NAME]
    assert 'description' in pkgs[utils._PKG_NAME]
    assert 'branches' in pkgs[utils._PKG_NAME]
    assert 'tags' in pkgs[utils._PKG_NAME]
