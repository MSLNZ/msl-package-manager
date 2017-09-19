"""
Command line interface for the ``list`` command.
"""
from .cli_argparse import add_argument_update_github_cache
from .print_packages import print_packages

HELP = 'Print the information about MSL packages.'

DESCRIPTION = HELP + """

The information can be either for the installed packages or 
for the packages that are available as GitHub repositories at 
https://github.com/MSLNZ, which can be installed (see "msl install").
"""

EXAMPLE = """
Examples:
    msl list
    msl list --github
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
        '-g', '--github',
        action='store_true',
        default=False,
        help='Print the information about the GitHub repositories.'
    )
    p.add_argument(
        '-d', '--detailed',
        action='store_true',
        default=False,
        help='Print the detailed information about the packages.'
    )
    add_argument_update_github_cache(p)
    p.set_defaults(func=execute)


def execute(args, parser):
    """Executes the ``list`` command."""
    print_packages(args.github, args.update_github_cache, args.detailed)
