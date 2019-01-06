"""
Command line interface for the :ref:`authorize <authorize_cli>` command.
"""
import getpass

from .utils import log, get_username, _get_input, _GITHUB_AUTH_PATH
from .cli_argparse import add_argument_quiet
from .cli_argparse import add_argument_disable_mslpm_version_check

WARNING_MESSAGE = """
Your username and password are saved in plain text in the file that
is created. You should set the file permissions provided by your 
operating system to ensure that your GitHub credentials are safe.
"""

HELP = 'Enable GitHub authorization.'

DESCRIPTION = HELP + """

When requesting information about the MSL repositories that are
available on GitHub there is a limit to how often you can send
requests to the GitHub API. If you have a GitHub account and 
include your username and password with each request then this 
limit is increased.

Running this command will create a file that contains your GitHub
username and password so that your GitHub requests are authorized.

**************************** IMPORTANT ****************************
{}
*******************************************************************
""".format(WARNING_MESSAGE)

EXAMPLE = """
Example:

  $ msl authorize
"""


def add_parser_authorize(parser):
    """Add the :ref:`authorize <authorize_cli>` command to the parser."""
    p = parser.add_parser(
        'authorize',
        help=HELP,
        description=DESCRIPTION,
        epilog=EXAMPLE,
    )
    add_argument_quiet(p)
    add_argument_disable_mslpm_version_check(p)
    p.set_defaults(func=execute)


def execute(args, parser):
    """Executes the :ref:`authorize <authorize_cli>` command."""
    default = get_username()
    try:
        username = _get_input('Enter your GitHub username [default: {}]: '.format(default))
    except KeyboardInterrupt:
        log.warning('\nDid not create GitHub authorization file.')
        return

    if not username:
        username = default

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
