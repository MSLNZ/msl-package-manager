import sys

from msl.package_manager import (
    pypi,
    github,
)

if not pypi() and not pypi(update_cache=True):
    sys.exit('Cannot update PyPI cache')

if not github() and not github(update_cache=True):
    sys.exit('Cannot update GitHub cache')
