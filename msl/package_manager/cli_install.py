"""
Command line interface for the :ref:`install <install_cli>` command.
"""
from .cli_argparse import add_argument_all
from .cli_argparse import add_argument_branch
from .cli_argparse import add_argument_package_names
from .cli_argparse import add_argument_tag
from .cli_argparse import add_argument_quiet
from .cli_argparse import add_argument_update_cache
from .cli_argparse import add_argument_yes
from .cli_argparse import add_argument_disable_mslpm_version_check
from .install import install

HELP = 'Install MSL packages.'

DESCRIPTION = HELP + """

MSL packages are retrieved from GitHub repositories or from PyPI.
"""

EXAMPLE = """
Examples:
    msl install equipment
    msl install loadlib --tag v0.3.0
"""


def add_parser_install(parser):
    """Add the :ref:`install <install_cli>` command to the parser."""
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
    add_argument_quiet(p)
    add_argument_update_cache(p)
    add_argument_disable_mslpm_version_check(p)
    p.set_defaults(func=execute)


def execute(args, parser):
    """Executes the :ref:`install <install_cli>` command."""
    if parser.contains_package_names():
        install(*args.names, yes=args.yes, branch=args.branch, tag=args.tag, update_cache=args.update_cache)
