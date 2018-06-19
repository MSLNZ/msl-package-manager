"""
Main entry point to either install, uninstall, update, list or create MSL packages
using the command-line interface (CLI).
"""
import sys
from pkg_resources import parse_version

from . import PKG_NAME, __version__
from . import utils

PARSER = None


def configure_parser():
    """:class:`~msl.package_manager.cli_argparse.ArgumentParser`: Returns the argument parser."""

    # pretty much mimics the ArgumentParser structure used by conda

    global PARSER
    if PARSER is not None:
        return PARSER

    from .cli_argparse import ArgumentParser
    from .cli_install import add_parser_install
    from .cli_uninstall import add_parser_uninstall
    from .cli_update import add_parser_update
    from .cli_list import add_parser_list
    from .cli_create import add_parser_create

    PARSER = ArgumentParser(description='Install, uninstall, update, list or create MSL packages.')

    PARSER.add_argument(
        '-V', '--version',
        action='version',
        version='{} {}'.format(PKG_NAME, __version__),
        help='Show the MSL Package Manager version number and exit.'
    )

    command_parser = PARSER.add_subparsers(
        metavar='command',
        dest='cmd',
    )
    # http://bugs.python.org/issue9253
    # http://stackoverflow.com/a/18283730/1599393
    command_parser.required = True

    add_parser_install(command_parser)
    add_parser_uninstall(command_parser)
    add_parser_uninstall(command_parser, 'remove')
    add_parser_update(command_parser)
    add_parser_update(command_parser, 'upgrade')
    add_parser_list(command_parser)
    add_parser_create(command_parser)

    return PARSER


def main(*args):
    """
    Main entry point to either install, uninstall, update, list or create MSL packages using the CLI.
    """
    if not args:
        args = sys.argv[1:]
        if not args:
            args = ['--help']
    parser = configure_parser()
    args = parser.parse_args(args)
    args.func(args, parser)

    pkgs = utils.pypi(quiet=True)
    latest = pkgs[PKG_NAME]['version']
    if parse_version(latest) > parse_version(__version__):
        utils._print_warning('\nYou are using {0} version {1}, however, version {2} is available.\n'
                             'You should consider upgrading via the "pip install -U {0}" command.' \
                             .format(PKG_NAME, __version__, latest))

    sys.exit(0)


if __name__ == '__main__':
    main()
