"""
Command line interface for the ``uninstall`` command.
"""
from .cli_argparse import add_argument_all
from .cli_argparse import add_argument_package_names
from .cli_argparse import add_argument_yes
from .uninstall import uninstall

DESCRIPTION = '{} MSL packages.'

EXAMPLE = """
Examples:
    msl {} loadlib
"""


def add_parser_uninstall(parser, name='uninstall'):
    """Add an ``uninstall`` command to the parser."""
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
    p.set_defaults(func=execute)


def execute(args, parser):
    """Executes the ``uninstall`` command."""
    if parser.contains_package_names():
        uninstall(*args.names, yes=args.yes)
