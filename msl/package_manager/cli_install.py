"""
Command line interface for the ``install`` command.
"""
from .cli_argparse import add_argument_all
from .cli_argparse import add_argument_branch
from .cli_argparse import add_argument_package_names
from .cli_argparse import add_argument_tag
from .cli_argparse import add_argument_update_github_cache
from .cli_argparse import add_argument_yes
from .install import install

HELP = 'Install MSL packages.'

DESCRIPTION = HELP + """

MSL packages are retrieved from GitHub repositories at https://github.com/MSLNZ
"""

EXAMPLE = """
Examples:
    msl install equipment
    msl install loadlib --tag v0.3.0
"""


def add_parser_install(parser):
    """Add an ``install`` command to the parser."""
    p = parser.add_parser(
        'install',
        help=HELP,
        description=DESCRIPTION,
        epilog=EXAMPLE,
    )
    add_argument_package_names(p)
    add_argument_all(p)
    add_argument_yes(p)
    add_argument_tag(p)
    add_argument_branch(p)
    add_argument_update_github_cache(p)
    p.set_defaults(func=execute)


def execute(args, parser):
    """Executes the ``install`` command."""
    if parser.contains_package_names():
        install(args.names, args.yes, args.update_github_cache, args.branch, args.tag)
