"""
Command line interface for the :ref:`authorise <authorise-cli>` command.
"""
from .authorise import WARNING_MESSAGE
from .authorise import authorise
from .cli_argparse import add_argument_disable_mslpm_version_check
from .cli_argparse import add_argument_quiet

HELP = 'Enable authorisation to the GitHub API.'

DESCRIPTION = HELP + """

When requesting information about the MSL repositories that are
available on GitHub there is a limit to how often you can send
requests to the GitHub API. If you have a GitHub account and 
include your username and a personal access token with each 
request then this limit is increased.

Running this command will create a file that contains your GitHub
username and a personal access token so that requests to the GitHub
API are authorised.

***************************** IMPORTANT ******************************
{}
**********************************************************************
""".format(WARNING_MESSAGE)

EXAMPLE = """
Example:

  $ msl {}
"""


def add_parser_authorise(parser, name='authorise'):
    """Add the :ref:`authorise <authorise-cli>` command to the parser."""
    p = parser.add_parser(
        name,
        help=HELP if name == 'authorise' else 'Alias for authorise.',
        description=DESCRIPTION,
        epilog=EXAMPLE.format(name),
    )
    add_argument_quiet(p)
    add_argument_disable_mslpm_version_check(p)
    p.set_defaults(func=execute)


def execute(args, parser):
    """Executes the :ref:`authorise <authorise-cli>` command."""
    print('For more detailed instructions on how to generate a personal access token see')
    print('https://docs.github.com/en/github/authenticating-to-github/creating-a-personal-access-token')
    print()
    print('To generate a personal access token, perform the following steps:')
    print('  1. Login to your GitHub account')
    print('  2. Go to Settings -> Developer settings -> Personal access tokens')
    print('  3. Click "Generate new token"')
    print('  4. In the "Note" field enter a description for the token (e.g., msl-package-manager)')
    print('  5. Select the expiration date of your token')
    print('  6. Optional: Select the scopes that you want to associate with the token')
    print('  7. Click "Generate token"')
    print('  8. Copy the token to your clipboard and paste it in the terminal when requested')
    print()
    authorise()
