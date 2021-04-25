import sys
import importlib

import pytest

from msl.package_manager import (
    install,
    installed,
    update,
    utils,
    uninstall,
)


def cleanup():
    msl_installed = installed()
    if 'msl-loadlib' in msl_installed:
        uninstall('loadlib', yes=True)
    if 'msl-io' in msl_installed:
        uninstall('io', yes=True)


def teardown_module():
    cleanup()


@pytest.mark.skipif(
    sys.version_info[:2] == (2, 7) and sys.platform == 'darwin',
    reason='hyphen gets appended to msl-loadlib version (0.7.0-)'
)
def test_update_msl_and_non_msl():
    cleanup()

    # msl-io has xlrd<2.0 as a dependency
    # make sure that xlrd is not >2.0 after updating

    install('loadlib==0.7.0', 'io', yes=True)

    mod = importlib.import_module('xlrd')
    assert mod.__version__ == '1.2.0'
    del mod

    outdated = utils.outdated_pypi_packages()
    assert 'msl-loadlib' not in outdated
    assert 'msl-io' not in outdated

    assert installed()['msl-loadlib']['version'] == '0.7.0'

    outdated.pop('pytest', None)
    outdated.pop('pytest-cov', None)

    update('loadlib==0.8.0', include_non_msl=True, yes=True)

    mod = importlib.import_module('xlrd')
    assert mod.__version__ == '1.2.0'
    del mod

    assert installed()['msl-loadlib']['version'] == '0.8.0'

    uninstall('loadlib', 'io', yes=True)
