import sys

import pytest

from msl.package_manager import (
    install,
    update,
    uninstall,
    installed,
)


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
