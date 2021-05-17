import io
import os
import sys
import time
import logging

from msl.package_manager import (
    pypi,
    github,
    utils,
)

logging.basicConfig(level=logging.DEBUG)

print('HOME_DIR: {}'.format(utils._HOME_DIR))

one_day = 60 * 60 * 24
github_cache = os.path.join(utils._HOME_DIR, 'github.json')
if os.path.isfile(github_cache):
    print('github_cache:\n{}\n{}'.format(time.time(), os.path.getmtime(github_cache) + one_day))
else:
    print('{!r} does not exist'.format(github_cache))

pypi_cache = os.path.join(utils._HOME_DIR, 'pypi.json')
if os.path.isfile(pypi_cache):
    print('pypi_cache:\n{}\n{}'.format(time.time(), os.path.getmtime(pypi_cache) + one_day))
else:
    print('{!r} does not exist'.format(pypi_cache))


pypi()
github()

# stream = io.BytesIO()
# handler = logging.StreamHandler(stream=stream)
#
# orig_level = int(utils.log.level)
# utils.set_log_level(logging.ERROR)
# utils.log.addHandler(handler)
#
# if not pypi():
#     pypi(update_cache=True)
#
# value = stream.getvalue()
# if value:
#     sys.exit('Cannot update PyPI cache\n{}'.format(value))
#
# if not github():
#     github(update_cache=True)
#
# value = stream.getvalue()
# if value:
#     sys.exit('Cannot update GitHub cache\n{}'.format(value))
#
# utils.log.removeHandler(handler)
# utils.set_log_level(orig_level)
# stream.close()
