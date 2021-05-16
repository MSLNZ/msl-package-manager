"""
Create an authorisation file for the GitHub API.
"""
from .utils import (
    log,
    get_username,
    _get_input,
    _GITHUB_AUTH_PATH,
)

WARNING_MESSAGE = """
Your username and personal access token are saved in plain text in the
file that is created. You should set the file permissions provided by 
your operating system to ensure that your GitHub credentials are safe.
"""


def authorise(username=None, token=None):
    """Create an authorisation file for the GitHub API.

    When requesting information about the MSL repositories_ that are
    available on GitHub there is a limit to how often you can send
    requests to the GitHub API. If you have a GitHub account and
    include your username and a `personal access token`_ with each
    request then this limit is increased.

    .. important::

       Calling this function will create a file that contains your GitHub
       username and a `personal access token`_ so that GitHub requests are
       authorised. Your username and `personal access token`_ are saved in
       plain text in the file that is created. You should set the file
       permissions provided by your operating system to ensure that your
       GitHub credentials are safe.

    .. versionadded:: 2.3.0

    .. versionchanged:: 2.4.0
        Renamed the `password` keyword argument to `token`.

    .. versionchanged:: 2.5.0
        Renamed function to `authorise`.

    .. _repositories: https://github.com/MSLNZ
    .. _personal access token: https://help.github.com/en/github/authenticating-to-github/creating-a-personal-access-token-for-the-command-line

    Parameters
    ----------
    username : :class:`str`, optional
        The GitHub username. If :data:`None` then you will be
        asked for the `username`.
    token : :class:`str`, optional
        A GitHub `personal access token`_ for `username`. If :data:`None`
        then you will be asked for the `token`.
    """
    if username is None:
        default = get_username()
        try:
            username = _get_input('Enter your GitHub username [default: {}]: '.format(default))
        except KeyboardInterrupt:
            log.warning('\nDid not create the GitHub authorisation file')
            return
        else:
            if not username:
                username = default

    if token is None:
        try:
            token = _get_input('Enter your GitHub personal access token: ')
        except KeyboardInterrupt:
            log.warning('\nDid not create the GitHub authorisation file')
            return

    if not username:
        log.warning('You must enter a username. Did not create the GitHub authorisation file')
        return

    if not token:
        log.warning('You must enter a personal access token. Did not create the GitHub authorisation file')
        return

    with open(_GITHUB_AUTH_PATH, 'w') as fp:
        fp.write(username + ':' + token)

    log.warning(WARNING_MESSAGE)
    log.info('GitHub credentials were saved to ' + _GITHUB_AUTH_PATH)
