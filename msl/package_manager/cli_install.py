"""
Command line interface for the :ref:`install <install-cli>` command.
"""
from .install import install
from .cli_argparse import (
    add_argument_all,
    add_argument_branch,
    add_argument_package_names,
    add_argument_tag,
    add_argument_quiet,
    add_argument_update_cache,
    add_argument_yes,
    add_argument_disable_mslpm_version_check,
)

HELP = 'Install MSL packages.'

DESCRIPTION = HELP + """

MSL packages are retrieved from GitHub repositories or from PyPI.
"""

EXAMPLE = """All other optional arguments are passed to "pip install".

Examples:
    msl install equipment
    msl install loadlib --tag v0.3.0
    msl install io network --retries 10
"""


def add_parser_install(parser):
    """Add the :ref:`install <install-cli>` command to the parser."""
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
    """Executes the :ref:`install <install-cli>` command."""
    if parser.contains_package_names():
        install(*args.names, yes=args.yes, branch=args.branch,
                tag=args.tag, update_cache=args.update_cache, pip_options=args.pip_options)
