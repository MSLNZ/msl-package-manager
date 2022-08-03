"""
Main entry point to either :ref:`install <install-cli>`, :ref:`uninstall <uninstall-cli>`,
:ref:`update <update-cli>`, :ref:`list <list-cli>` or :ref:`create <create-cli>`
MSL packages using the command-line interface (CLI).
"""
import os
import re
import sys
import logging
import subprocess
from pkg_resources import parse_version

from . import utils, __version__, _PKG_NAME

PARSER = None

_pip_options_regexg = re.compile(r'\s+(-[a-zA-Z])?,?\s+(--[-\w]+)\s+(<.*>)?\s')


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
    from .cli_authorise import add_parser_authorise

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
    add_parser_uninstall(command_parser, name='remove')
    add_parser_update(command_parser)
    add_parser_update(command_parser, name='upgrade')
    add_parser_list(command_parser)
    add_parser_create(command_parser)
    add_parser_authorise(command_parser)
    add_parser_authorise(command_parser, name='authorize')

    return PARSER


def parse_args(args):
    """Parse arguments.

    Parameters
    ----------
    args : :class:`list` of :class:`str`
        The arguments to parse.

    Returns
    -------
    An :class:`argparse.Namespace` or :data:`None` if there was an error.
    """
    def pip_options_valid(command):
        # returns either True or False
        valid_options = {}
        out = subprocess.check_output([sys.executable, '-m', 'pip', 'help', command], stderr=subprocess.PIPE)
        for short, long, value in _pip_options_regexg.findall(out.decode()):
            if short:
                valid_options[short] = value
            valid_options[long] = value

        pip_options_copy = pip_options[:]
        for i, option in enumerate(pip_options_copy):
            if not option.startswith('-'):
                # make sure the previous item in pip_options accepts a value
                # if it doesn't then append the option to parsed_args.names
                # because the name of an msl package got mistakenly added to pip_options
                if not valid_options.get(pip_options_copy[i-1]):
                    name = pip_options.pop(pip_options.index(option))
                    parsed_args.names.append(name)

            elif option not in valid_options:
                utils.log.error('No such option for "pip {}": {}'.format(command, option))
                return False

            # if the pip option requires a value then make sure the value did
            # not end up in the parsed_args.names list and the value comes
            # immediately after the appropriate item in the pip_options list
            elif valid_options[option]:
                arg_index = args.index(option) + 1
                pip_index = pip_options_copy.index(option) + 1
                if pip_index >= len(pip_options_copy) or args[arg_index] != pip_options_copy[pip_index]:
                    names_index = parsed_args.names.index(args[arg_index])
                    name = parsed_args.names.pop(names_index)
                    pip_options.insert(pip_index, name)

        return True

    parser = configure_parser()
    # Want to be able to support all options that "pip (un)install"
    # supports without depending on the version of pip that is installed.
    # There are possible 3 ways to do this:
    #   1) create a new argparse with nargs=*
    #   2) create a new argparse with nargs=REMAINDER
    #   3) use parse_known_args() instead of parse_args()
    # Option 3 was the preferred way because nargs=* and nargs=REMAINDER
    # each had their limitations.
    parsed_args, pip_options = parser.parse_known_args(args=args)

    if parsed_args.quiet == 0:
        utils.set_log_level(logging.DEBUG)
    elif parsed_args.quiet == 1:
        utils.set_log_level(logging.INFO)
    elif parsed_args.quiet == 2:
        utils.set_log_level(logging.WARNING)
    elif parsed_args.quiet == 3:
        utils.set_log_level(logging.ERROR)
    elif parsed_args.quiet == 4:
        utils.set_log_level(logging.CRITICAL + 1)

    if pip_options:
        if parsed_args.cmd in ['install', 'update', 'upgrade']:
            if not pip_options_valid('install'):
                return
        elif parsed_args.cmd in ['uninstall', 'remove']:
            if not pip_options_valid('uninstall'):
                return
        else:
            utils.log.warning('The following options are ignored: ' + ', '.join(p for p in pip_options))

    parsed_args.pip_options = pip_options
    return parsed_args


def _main(*args):
    # parse the input
    if not args:
        args = sys.argv[1:]
        if not args:
            args = ['--help']

    args = parse_args(args)
    if not args:
        return

    # when the msl-package-manager gets updated a msl.exe.old file gets created (on Windows)
    old = sys.exec_prefix + '/Scripts/msl.exe.old'
    if os.path.isfile(old):
        os.remove(old)

    # execute the command
    ret = args.func(args, PARSER)
    if ret == 'updating_msl_package_manager':
        return

    if args.disable_mslpm_version_check:
        return

    # check if there is an update for the MSL Package Manager
    # do not log any messages when checking for the update
    utils.set_log_level(logging.CRITICAL+1)
    pkgs = utils.pypi()
    if not pkgs:
        return

    latest = pkgs[_PKG_NAME]['version']
    if parse_version(latest) > parse_version(__version__):
        utils.set_log_level(logging.WARNING)
        utils.log.warning('You are using {0} version {1}, however, version {2} is available.\n'
                          'You should consider updating via the \'msl update package-manager\''
                          ' command.'.format(_PKG_NAME, __version__, latest))


def main(*args):
    """
    Main entry point to either :ref:`install <install-cli>`, :ref:`uninstall <uninstall-cli>`,
    :ref:`update <update-cli>`, :ref:`list <list-cli>` or :ref:`create <create-cli>`
    MSL packages using the CLI.
    """
    sys.exit(_main(*args))


if __name__ == '__main__':
    _main()
