"""
Command line interface for the :ref:`authorize <authorize_cli>` command.
"""
from .cli_argparse import add_argument_quiet
from .cli_argparse import add_argument_disable_mslpm_version_check
from .authorize import (
    WARNING_MESSAGE,
    authorize,
)

HELP = 'Enable GitHub authorization.'

DESCRIPTION = HELP + """

When requesting information about the MSL repositories that are
available on GitHub there is a limit to how often you can send
requests to the GitHub API. If you have a GitHub account and 
include your username and password with each request then this 
limit is increased.

Running this command will create a file that contains your GitHub
username and password so that GitHub requests are authorized.

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
    authorize()
