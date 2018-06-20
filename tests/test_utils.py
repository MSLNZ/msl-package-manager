import os
import sys
import logging
import tempfile

from msl.package_manager import utils

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

    utils.show_packages()
    lines = read_file_logger()
    assert os.path.dirname(sys.executable) in lines[0]

    utils.show_packages(from_github=True)
    lines = read_file_logger()
    assert 'cached' in lines[0]
    assert 'GitHub' in lines[0]

    utils.show_packages(from_pypi=True)
    lines = read_file_logger()
    assert 'cached' in lines[0]
    assert 'PyPI' in lines[0]


