"""
Command line interface for the ``update`` command.
"""
from .cli_argparse import add_argument_all
from .cli_argparse import add_argument_branch
from .cli_argparse import add_argument_package_names
from .cli_argparse import add_argument_tag
from .cli_argparse import add_argument_update_github_cache
from .cli_argparse import add_argument_yes
from .update import update

DESCRIPTION = """{} MSL packages.

MSL packages are retrieved from GitHub repositories at https://github.com/MSLNZ
"""

EXAMPLE = """
Examples:
    msl {0} equipment qt
    msl {0} loadlib --tag v0.3.0
"""


def add_parser_update(parser, name='update'):
    """Add an ``update`` command to the parser."""
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
    add_argument_update_github_cache(p)
    p.set_defaults(func=execute)


def execute(args, parser):
    """Executes the ``update`` command."""
    if parser.contains_package_names():
        update(args.names, args.yes, args.update_github_cache, args.branch, args.tag)
