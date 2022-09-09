import importlib
import sys
try:
    from importlib import reload
except ImportError:  # then Python 2
    from imp import reload

import pytest

from msl.package_manager import install
from msl.package_manager import installed
from msl.package_manager import uninstall
from msl.package_manager import update
from msl.package_manager import utils


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
def test_msl_and_non_msl():
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
        assert outdated['xlrd']['version'] == '<2.0'

    msl_loadlib = importlib.import_module('msl.loadlib')
    assert installed()['msl-loadlib']['version'] == '0.7.0'
    assert msl_loadlib.__version__ == '0.7.0'

    update('loadlib==0.8.0', include_non_msl=True, yes=True)

    assert reload(xlrd).__version__ == '1.2.0'

    assert installed()['msl-loadlib']['version'] == '0.8.0'
    assert reload(msl_loadlib).__version__ == '0.8.0'

    uninstall('loadlib', 'io', yes=True)
    installed_ = installed()
    assert 'msl-loadlib' not in installed_
    assert 'msl-io' not in installed_


def test_from_commit():
    cleanup()

    commit1 = 'b2581039e4e3f2ffe2599927d589809efbb9a1ff'
    commit2 = '12591bade80321c3a165f7a7364ef13f568d622b'

    install('loadlib', yes=True, commit=commit1)

    # reload all msl modules
    for name, module in sys.modules.copy().items():
        if name.startswith('msl'):
            try:
                reload(module)
            except:
                pass

    # the version ends with the expected commit hash
    packages = installed()
    expected = '0.9.0.dev0+{}'.format(commit1[:7])
    assert 'msl-loadlib' in packages
    assert packages['msl-loadlib']['version'] == expected
    msl_loadlib = importlib.import_module('msl.loadlib')
    assert msl_loadlib.__version__ == expected

    update('loadlib', yes=True, commit=commit2)

    # reload all msl modules
    for name, module in sys.modules.copy().items():
        if name.startswith('msl'):
            try:
                reload(module)
            except:
                pass

    # the version ends with the expected commit hash
    packages = installed()
    expected = '0.9.1.dev0+{}'.format(commit2[:7])
    assert 'msl-loadlib' in packages
    assert packages['msl-loadlib']['version'] == expected
    msl_loadlib = importlib.import_module('msl.loadlib')
    assert msl_loadlib.__version__ == expected

    uninstall('loadlib', yes=True)
    assert 'msl-loadlib' not in installed()
