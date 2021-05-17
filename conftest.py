import sys

from msl.package_manager import (
    pypi,
    github,
)

if not pypi():
    sys.exit('Cannot load the PyPI cache')

if not github():
    sys.exit('Cannot load the GitHub cache')
