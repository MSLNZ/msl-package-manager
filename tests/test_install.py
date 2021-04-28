import re
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
    uninstall,
)


def cleanup():
    if 'msl-loadlib' in installed():
        uninstall('msl-loadlib', yes=True)


def teardown_module():
    cleanup()


@pytest.mark.skipif(
    sys.version_info[:2] == (2, 7) and sys.platform == 'darwin',
    reason='hyphen gets appended to msl-loadlib version (0.7.0-)'
)
def test_version_suffix():
    cleanup()

    install('loadlib==0.7.0', yes=True)

    # reload all msl modules
    for name, module in sys.modules.copy().items():
        if name.startswith('msl'):
            try:
                reload(module)
            except:
                pass

    packages = installed()

    # the version does not end with a commit hash
    assert 'msl-loadlib' in packages
    assert packages['msl-loadlib']['version'] == '0.7.0'
    msl_loadlib = importlib.import_module('msl.loadlib')
    assert msl_loadlib.__version__ == '0.7.0'

    # msl-package-manager gets installed in editable mode (pip install -e)
    # in cloud-based testing platforms
    if 'msl-package-manager' in packages:
        assert packages['msl-package-manager']['version'].endswith('+editable')

    uninstall('loadlib', yes=True)
    assert 'msl-loadlib' not in installed()

    install('loadlib', branch='main', yes=True)
    packages = installed()

    # the version ends with a commit hash
    assert 'msl-loadlib' in packages
    version = packages['msl-loadlib']['version']
    assert re.search(r'\+[a-z0-9]{7}$', version)
    assert reload(msl_loadlib).__version__ == version

    uninstall('loadlib', yes=True)
    assert 'msl-loadlib' not in installed()
