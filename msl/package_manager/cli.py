"""
Main entry point to either :ref:`install <install_cli>`, :ref:`uninstall <uninstall_cli>`,
:ref:`update <update_cli>`, :ref:`list <list_cli>` or :ref:`create <create_cli>`
MSL packages using the command-line interface (CLI).
"""
import os
import sys
import logging
from pkg_resources import parse_version

from . import utils, __version__, _PKG_NAME

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
    from .cli_authorize import add_parser_authorize

    PARSER = ArgumentParser(description='Install, uninstall, update, list or create MSL packages.')

    PARSER.add_argument(
        '-V', '--version',
        action='version',
        version='{} {}'.format(_PKG_NAME, __version__),
        help='Show the MSL Package Manager version number and exit.'
    )

    command_parser = PARSER.add_subparsers(
        metavar='command',
        dest='cmd',
    )
    # https://bugs.python.org/issue9253
    # https://stackoverflow.com/a/18283730/1599393
    command_parser.required = True

    add_parser_install(command_parser)
    add_parser_uninstall(command_parser)
    add_parser_uninstall(command_parser, 'remove')
    add_parser_update(command_parser)
    add_parser_update(command_parser, 'upgrade')
    add_parser_list(command_parser)
    add_parser_create(command_parser)
    add_parser_authorize(command_parser)

    return PARSER


def _main(*args):
    # parse the input
    if not args:
        args = sys.argv[1:]
        if not args:
            args = ['--help']

    parser = configure_parser()
    args = parser.parse_args(args)

    if args.quiet == 1:
        utils.set_log_level(logging.ERROR)
    elif args.quiet == 2:
        utils.set_log_level(logging.CRITICAL)
    elif args.quiet == 3:
        utils.set_log_level(logging.CRITICAL + 1)

    # when the msl-package-manager gets updated a msl.exe.old file gets created
    old = sys.exec_prefix + '/Scripts/msl.exe.old'
    if os.path.isfile(old):
        os.remove(old)

    # execute the command
    ret = args.func(args, parser)
    if ret == 'updating_msl_package_manager':
        return

    if args.disable_mslpm_version_check:
        return

    # check if there is an update for the MSL Package Manager
    if utils.log.level < logging.WARNING:  # do not log DEBUG messages when checking for the update
        utils.set_log_level(logging.WARNING)

    pkgs = utils.pypi()
    if not pkgs:
        return

    latest = pkgs[_PKG_NAME]['version']
    if parse_version(latest) > parse_version(__version__):
        utils.log.warning('You are using {0} version {1}, however, version {2} is available.\n'
                          'You should consider upgrading via the \'msl update package-manager\''
                          ' command.'.format(_PKG_NAME, __version__, latest))


def main(*args):
    """
    Main entry point to either :ref:`install <install_cli>`, :ref:`uninstall <uninstall_cli>`,
    :ref:`update <update_cli>`, :ref:`list <list_cli>` or :ref:`create <create_cli>`
    MSL packages using the CLI.
    """
    sys.exit(_main(*args))


if __name__ == '__main__':
    _main()
