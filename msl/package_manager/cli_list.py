"""
Command line interface for the ``list`` command.
"""
from .cli_argparse import add_argument_update_cache
from .cli_argparse import add_argument_quiet
from .utils import show_packages

HELP = 'Show the information about MSL packages.'

DESCRIPTION = HELP + """

The information can be either for the installed packages,  
packages that are available as GitHub repositories, or
packages available on PyPI.
"""

EXAMPLE = """
Examples:
    msl list
    msl list --github --detailed
    msl list --pypi
"""


def add_parser_list(parser):
    """Add a ``list`` command to the parser."""
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
        '-d', '--detailed',
        action='store_true',
        default=False,
        help='Show the detailed information, includes information\n'
             'about the branches and tags, for the GitHub\n'
             'repositories in JSON format.'
    )
    add_argument_quiet(p)
    add_argument_update_cache(p)
    p.set_defaults(func=execute)


def execute(args, parser):
    """Executes the ``list`` command."""
    show_packages(args.github, args.detailed, args.pypi, args.update_cache)
