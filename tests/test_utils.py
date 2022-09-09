import logging
import os
import sys

from msl.package_manager import utils


# see the docs for the caplog fixture
# https://docs.pytest.org/en/latest/logging.html#caplog-fixture
def test_info_log(caplog):
    # checks that the logging messages have the expected output
    caplog.set_level(logging.DEBUG, logger=utils._PKG_NAME)
    exec_path = os.path.dirname(sys.executable)

    utils.info()
    expected = [
        'Getting the packages from {}'.format(exec_path),
    ]
    for index, message in enumerate(expected):
        assert caplog.records[index].message == message
    del caplog.records[:]

    utils.info(from_github=True)
    expected = [
        'Loaded the cached information about the GitHub repositories',
    ]
    for index, message in enumerate(expected):
        assert caplog.records[index].message == message
    del caplog.records[:]

    utils.info(from_pypi=True)
    expected = [
        'Loaded the cached information about the PyPI packages',
    ]
    for index, message in enumerate(expected):
        assert caplog.records[index].message == message
    del caplog.records[:]


def test_create_install_list():

    # args -> names, branch, tag, update_cache

    pkgs = utils._create_install_list((), None, None, None, False)
    for p in pkgs:
        assert p.startswith('msl-')
    assert utils._PKG_NAME not in pkgs

    # "msl-" prefix gets added
    pkgs = utils._create_install_list(('loadlib', 'network'), None, None, None, False)
    assert len(pkgs) == 2
    assert 'msl-loadlib' in pkgs
    assert 'msl-network' in pkgs

    # case insensitive
    pkgs = utils._create_install_list(('MSL-loadlib', 'network', 'gtc'), None, None, None, False)
    assert len(pkgs) == 3
    assert 'msl-loadlib' in pkgs
    assert 'msl-network' in pkgs
    assert 'GTC' in pkgs

    # msl-network does not show up twice
    pkgs = utils._create_install_list(('loadlib', 'msl-network', 'network', 'pr-omega-logger'), None, None, None, False)
    assert len(pkgs) == 3
    assert 'msl-loadlib' in pkgs
    assert 'msl-network' in pkgs
    assert 'pr-omega-logger' in pkgs

    # all repos that start with "pr-"
    pkgs = utils._create_install_list(('pr-*',), None, None, None, False)
    assert len(pkgs) >= 1
    assert 'pr-omega-logger' in pkgs
    for p in pkgs:
        assert p.startswith('pr-')

    # all Python repos
    pkgs = utils._create_install_list(('*',), None, None, None, False)
    assert 'msl-loadlib' in pkgs
    assert 'hs-logger' in pkgs
    assert 'pr-omega-logger' in pkgs
    assert 'GTC' in pkgs
    assert 'Lengthstds_Environment_Monitoring' not in pkgs  # it's written in C# not Python

    # the asterisk appears first before any other character
    pkgs = utils._create_install_list(('*loadlib',), None, None, None, False)
    assert len(pkgs) == 1
    assert pkgs['msl-loadlib']['version_requested'] is None
    assert pkgs['msl-loadlib']['extras_require'] is None

    #
    # support for extras_require and version ranges
    #
    names = ('loadlib[clr]', 'gtc', 'Lengthstds_Environment_Monitoring', 'Does Not Exist', 'msl-network==0.4')
    pkgs = utils._create_install_list(names, None, None, None, False)
    assert len(pkgs) == 3
    assert 'msl-loadlib' in pkgs
    assert 'GTC' in pkgs
    assert 'msl-network' in pkgs
    assert 'Lengthstds_Environment_Monitoring' not in pkgs  # it's written in C# not Python
    assert 'Does Not Exist' not in pkgs
    assert pkgs['msl-loadlib']['extras_require'] == '[clr]'
    assert pkgs['msl-loadlib']['version_requested'] is None
    assert pkgs['msl-network']['extras_require'] is None
    assert pkgs['msl-network']['version_requested'] == '==0.4'

    names = ('msl-loadlib[java,clr]>=0.4,<0.6', 'GtC==1.1.*', 'network!=0.4.0', 'ms*qt[pyside]==0.1.0.dev0')
    pkgs = utils._create_install_list(names, None, None, None, False)
    assert len(pkgs) == 4
    assert pkgs['msl-loadlib']['extras_require'] == '[java,clr]'
    assert pkgs['msl-loadlib']['version_requested'] == '>=0.4,<0.6'
    assert pkgs['GTC']['extras_require'] is None
    assert pkgs['GTC']['version_requested'] == '==1.1.*'
    assert pkgs['msl-network']['extras_require'] is None
    assert pkgs['msl-network']['version_requested'] == '!=0.4.0'
    assert pkgs['msl-qt']['extras_require'] == '[pyside]'
    assert pkgs['msl-qt']['version_requested'] == '==0.1.0.dev0'


def test_has_git():
    assert utils.has_git


def test_outdated_pypi_packages():
    outdated = utils.outdated_pypi_packages()
    for info in outdated.values():
        assert info['installed_version']
        assert isinstance(info['using_pypi'], bool) and info['using_pypi']
        assert info['extras_require'] == ''
        assert info['version']
        assert info['repo_name'] == ''
