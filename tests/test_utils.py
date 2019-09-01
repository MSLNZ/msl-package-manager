import os
import sys
import logging
import tempfile

from msl.package_manager import utils, _PKG_NAME

file_logger = None


def create_file_logger():
    global file_logger

    if file_logger is not None:
        return file_logger

    file_logger = logging.FileHandler(
        filename=os.path.join(tempfile.gettempdir(), 'msl-package-manager-testing.log'),
        mode='w',
    )
    file_logger.setLevel(logging.DEBUG)
    file_logger.setFormatter(logging.Formatter('%(message)s'))
    utils.log.addHandler(file_logger)

    return file_logger


def read_file_logger():
    file_logger.close()
    with open(file_logger.baseFilename, 'rt') as fp:
        lines = fp.readlines()
    return lines


def setup_module(module):
    utils.set_log_level(logging.DEBUG)
    create_file_logger()


def teardown_module(module):
    global file_logger
    file_logger.close()
    os.remove(file_logger.baseFilename)
    file_logger = None


def test_show_packages():

    utils.info()
    lines = read_file_logger()
    assert os.path.dirname(sys.executable) in lines[0]

    utils.info(from_github=True)
    lines = read_file_logger()
    assert 'cached' in lines[0]
    assert 'GitHub' in lines[0]

    utils.info(from_pypi=True)
    lines = read_file_logger()
    assert 'cached' in lines[0]
    assert 'PyPI' in lines[0]


def test_create_install_list():

    # args -> names, branch, tag, update_cache

    pkgs = utils._create_install_list((), None, None, False)
    for p in pkgs:
        assert p.startswith('msl-')
    assert _PKG_NAME not in pkgs

    # "msl-" prefix gets added
    pkgs = utils._create_install_list(('loadlib', 'network'), None, None, False)
    assert len(pkgs) == 2
    assert 'msl-loadlib' in pkgs
    assert 'msl-network' in pkgs

    # case insensitive
    pkgs = utils._create_install_list(('MSL-loadlib', 'network', 'gtc'), None, None, False)
    assert len(pkgs) == 3
    assert 'msl-loadlib' in pkgs
    assert 'msl-network' in pkgs
    assert 'GTC' in pkgs

    # msl-network does not show up twice
    pkgs = utils._create_install_list(('loadlib', 'msl-network', 'network', 'pr-omega-logger'), None, None, False)
    assert len(pkgs) == 3
    assert 'msl-loadlib' in pkgs
    assert 'msl-network' in pkgs
    assert 'pr-omega-logger' in pkgs

    # all repos that start with "pr-"
    pkgs = utils._create_install_list(('pr-*',), None, None, False)
    assert len(pkgs) >= 1
    assert 'pr-omega-logger' in pkgs
    for p in pkgs:
        assert p.startswith('pr-')

    # all Python repos
    pkgs = utils._create_install_list(('*',), None, None, False)
    assert 'msl-loadlib' in pkgs
    assert 'hs-logger' in pkgs
    assert 'pr-omega-logger' in pkgs
    assert 'GTC' in pkgs
    assert 'Lengthstds_Environment_Monitoring' not in pkgs  # it's written in C# not Python

    # the asterisk appears first before any other character
    pkgs = utils._create_install_list(('*loadlib',), None, None, False)
    assert len(pkgs) == 1
    assert pkgs['msl-loadlib']['version_requested'] is None
    assert pkgs['msl-loadlib']['extras_require'] is None

    #
    # support for extras_require and version ranges
    #
    names = ('loadlib[clr]', 'gtc', 'Lengthstds_Environment_Monitoring', 'Does Not Exist', 'msl-network==0.4')
    pkgs = utils._create_install_list(names, None, None, False)
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
    pkgs = utils._create_install_list(names, None, None, False)
    assert len(pkgs) == 4
    assert pkgs['msl-loadlib']['extras_require'] == '[java,clr]'
    assert pkgs['msl-loadlib']['version_requested'] == '>=0.4,<0.6'
    assert pkgs['GTC']['extras_require'] is None
    assert pkgs['GTC']['version_requested'] == '==1.1.*'
    assert pkgs['msl-network']['extras_require'] is None
    assert pkgs['msl-network']['version_requested'] == '!=0.4.0'
    assert pkgs['msl-qt']['extras_require'] == '[pyside]'
    assert pkgs['msl-qt']['version_requested'] == '==0.1.0.dev0'
