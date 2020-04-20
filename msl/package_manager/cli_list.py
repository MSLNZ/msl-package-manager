"""
Command line interface for the :ref:`list <list-cli>` command.
"""
from .utils import info
from .cli_argparse import (
    add_argument_update_cache,
    add_argument_quiet,
    add_argument_disable_mslpm_version_check,
)

HELP = 'Show the information about MSL packages.'

DESCRIPTION = HELP + """

The information can be either for the installed packages,  
packages that are available as GitHub repositories, or
packages available on PyPI.
"""

EXAMPLE = """
Examples:
    msl list
    msl list --github --json
    msl list --pypi
"""


def add_parser_list(parser):
    """Add the :ref:`list <list-cli>` command to the parser."""
    p = parser.add_parser(
        'list',
        help=HELP,
        description=DESCRIPTION,
        epilog=EXAMPLE,
    )
    p.add_argument(
        '-p', '--pypi',
        action='store_true',
        default=False,
        help='Show the information about the PyPI packages.'
    )
    p.add_argument(
        '-g', '--github',
        action='store_true',
        default=False,
        help='Show the information about the GitHub repositories.'
    )
    p.add_argument(
        '-j', '--json',
        action='store_true',
        default=False,
        help='Show the information in JSON format.\n'
             'For the GitHub repositories this includes additional\n'
             'information about the branches and tags.'
    )
    add_argument_quiet(p)
    add_argument_update_cache(p)
    add_argument_disable_mslpm_version_check(p)
    p.set_defaults(func=execute)


def execute(args, parser):
    """Executes the :ref:`list <list-cli>` command."""
    info(args.github, args.pypi, args.update_cache, args.json)
