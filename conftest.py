import io
import sys
import logging

from msl.package_manager import (
    pypi,
    github,
    utils,
)

stream = io.BytesIO()
handler = logging.StreamHandler(stream=stream)

orig_level = int(utils.log.level)
utils.set_log_level(logging.ERROR)
utils.log.addHandler(handler)

if not pypi():
    pypi(update_cache=True)

if stream.getbuffer():
    sys.exit('Cannot update PyPI cache')

if not github():
    github(update_cache=True)

if stream.getbuffer():
    sys.exit('Cannot update GitHub cache')

utils.log.removeHandler(handler)
utils.set_log_level(orig_level)
stream.close()
