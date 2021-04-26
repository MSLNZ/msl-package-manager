import sys
import importlib
try:
    from importlib import reload
except ImportError:  # then Python 2
    from imp import reload

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

    # reload all msl modules
    for name, module in sys.modules.copy().items():
        if name.startswith('msl'):
            try:
                reload(module)
            except:
                pass

    xlrd = importlib.import_module('xlrd')
    assert xlrd.__version__ == '1.2.0'

    outdated = utils.outdated_pypi_packages()
    assert 'msl-loadlib' not in outdated
    assert 'msl-io' not in outdated

    # strange, this assert fails in Python 3.5 and does not
    # depend on the version of pip (checked back to pip 10.0)
    if sys.version_info[:2] != (3, 5):
        assert 'xlrd' in outdated

    msl_loadlib = importlib.import_module('msl.loadlib')
    assert installed()['msl-loadlib']['version'] == '0.7.0'
    assert msl_loadlib.__version__ == '0.7.0'

    update('loadlib==0.8.0', include_non_msl=True, yes=True)

    assert reload(xlrd).__version__ == '1.2.0'

    assert installed()['msl-loadlib']['version'] == '0.8.0'
    assert reload(msl_loadlib).__version__ == '0.8.0'

    uninstall('loadlib', 'io', yes=True)
