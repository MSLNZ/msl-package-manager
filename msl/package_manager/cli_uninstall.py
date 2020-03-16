"""
Command line interface for the :ref:`uninstall <uninstall_cli>` command.
"""
from .uninstall import uninstall
from .cli_argparse import (
    add_argument_all,
    add_argument_package_names,
    add_argument_yes,
    add_argument_quiet,
    add_argument_disable_mslpm_version_check,
)

DESCRIPTION = '{} MSL packages.'

EXAMPLE = """All other optional arguments are passed to "pip uninstall".

Examples:
    msl {0} loadlib
    msl {0} qt --no-python-version-warning
"""


def add_parser_uninstall(parser, name='uninstall'):
    """Add the :ref:`uninstall <uninstall_cli>` command to the parser."""
    if name == 'uninstall':
        p = parser.add_parser(
            name,
            help='Uninstall MSL packages.',
            description=DESCRIPTION.format(name.capitalize()),
            epilog=EXAMPLE.format(name),
        )
    else:
        p = parser.add_parser(
            name,
            help='Alias for uninstall.',
            description=DESCRIPTION.format(name.capitalize()),
            epilog=EXAMPLE.format(name),
        )
    add_argument_package_names(p)
    add_argument_all(p)
    add_argument_yes(p)
    add_argument_quiet(p)
    add_argument_disable_mslpm_version_check(p)
    p.set_defaults(func=execute)


def execute(args, parser):
    """Executes the :ref:`uninstall <uninstall_cli>` command."""
    if parser.contains_package_names():
        uninstall(*args.names, yes=args.yes, pip_options=args.pip_options)
