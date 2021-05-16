import io
import sys
import logging

from msl.package_manager import (
    pypi,
    github,
    utils,
)

print('HOME_DIR: {}'.format(utils._HOME_DIR))
print('AUTH_PATH: {}'.format(utils._GITHUB_AUTH_PATH))

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
