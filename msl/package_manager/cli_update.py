"""
Command line interface for the :ref:`update <update-cli>` command.
"""
from .update import update
from .cli_argparse import (
    add_argument_all,
    add_argument_branch,
    add_argument_package_names,
    add_argument_tag,
    add_argument_update_cache,
    add_argument_yes,
    add_argument_quiet,
    add_argument_disable_mslpm_version_check,
)

DESCRIPTION = """{} MSL packages.

MSL packages are retrieved from GitHub repositories or from PyPI.
"""

EXAMPLE = """All other optional arguments are passed to "pip install --upgrade".

Examples:
    msl {0} equipment qt
    msl {0} loadlib --tag v0.3.0
    msl {0} io --no-deps
"""


def add_parser_update(parser, name='update'):
    """Add the :ref:`update <update-cli>` command to the parser."""
    if name == 'update':
        p = parser.add_parser(
            name,
            help='Update MSL packages.',
            description=DESCRIPTION.format(name.capitalize()),
            epilog=EXAMPLE.format(name),
        )
    else:
        p = parser.add_parser(
            name,
            help='Alias for update.',
            description=DESCRIPTION.format(name.capitalize()),
            epilog=EXAMPLE.format(name),
        )
    add_argument_package_names(p)
    add_argument_all(p)
    add_argument_yes(p)
    add_argument_tag(p)
    add_argument_branch(p)
    add_argument_quiet(p)
    add_argument_update_cache(p)
    add_argument_disable_mslpm_version_check(p)
    p.add_argument(
        '-o', '--non-msl',
        action='store_true',
        default=False,
        help='{} all non-MSL packages that are outdated.\n'
             'Warning, use this option with caution.'.format(name.title())
    )
    p.set_defaults(func=execute)


def execute(args, parser):
    """Executes the :ref:`update <update-cli>` command."""
    if parser.contains_package_names(quiet=args.non_msl) or args.non_msl:
        return update(
            *args.names,
            yes=args.yes,
            branch=args.branch,
            tag=args.tag,
            update_cache=args.update_cache,
            pip_options=args.pip_options,
            include_non_msl=args.non_msl
        )
