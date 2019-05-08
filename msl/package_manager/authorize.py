"""
Create the GitHub authorization file.
"""
import getpass

from .utils import log, get_username, _get_input, _GITHUB_AUTH_PATH

WARNING_MESSAGE = """
Your username and password are saved in plain text in the file that
is created. You should set the file permissions provided by your 
operating system to ensure that your GitHub credentials are safe.
"""


def authorize(username=None, password=None):
    """
    Create the GitHub authorization file.

    When requesting information about the MSL repositories_ that are
    available on GitHub there is a limit to how often you can send
    requests to the GitHub API. If you have a GitHub account and
    include your username and password with each request then this
    limit is increased.

    Calling this function will create a file that contains your GitHub
    username and password so that GitHub requests are authorized.

    .. versionadded:: 2.3.0

    .. _repositories: https://github.com/MSLNZ

    Parameters
    ----------
    username : :class:`str`, optional
        The GitHub username. If :data:`None` then you will be
        asked for the `username`.
    password : :class:`str`, optional
        The GitHub password. If :data:`None` then you will be
        asked for the `password`.
    """
    if username is None:
        default = get_username()
        try:
            username = _get_input('Enter your GitHub username [default: {}]: '.format(default))
        except KeyboardInterrupt:
            log.warning('\nDid not create GitHub authorization file.')
            return
        else:
            if not username:
                username = default

    if password is None:
        try:
            password = getpass.getpass('Enter your GitHub password: ')
        except KeyboardInterrupt:
            log.warning('\nDid not create GitHub authorization file.')
            return

    if not password:
        log.warning('You must enter a password. Did not create GitHub authorization file.')
        return

    with open(_GITHUB_AUTH_PATH, 'w') as fp:
        fp.write(username + ':' + password)

    log.warning(WARNING_MESSAGE)
    log.info('GitHub credentials saved to ' + _GITHUB_AUTH_PATH)
