"""
Main entry point to either install, uninstall, list or create MSL packages
using the command-line interface (CLI).
"""
import sys
import argparse

from .install import install
from .uninstall import uninstall
from .create import create
from .print_list import print_list


def main():
    """
    Main entry point to either install, uninstall, list or create MSL packages using the CLI.

    **This function should not be called directly as it is the main entry point for the CLI.**
    """
    parser = argparse.ArgumentParser(description='Manage MSL packages')

    parser.add_argument('command',
                        help='the command to run [install, uninstall, create, list]')

    parser.add_argument('names',
                        help='the name(s) of the MSL package(s)', nargs='*')

    parser.add_argument('-a', '--author', nargs='+',
                        help="the name of the author [used by 'create']")

    parser.add_argument('-e', '--email',
                        help="the email address for the author [used by 'create']")

    parser.add_argument('-y', '--yes', action='store_true',
                        help="don't ask for confirmation to (un)install")

    parser.add_argument('-r', '--release-info', action='store_true',
                        help="include the release info from GitHub [used by 'list', takes longer to execute]")

    args = parser.parse_args()

    args.command = args.command.lower()

    if args.command == 'install':
        install(args.names if args.names else 'ALL', args.yes)

    elif args.command == 'uninstall':
        uninstall(args.names if args.names else 'ALL', args.yes)

    elif args.command == 'create':
        create(args.names, args.author, args.email)

    elif args.command == 'list':
        if (len(args.names) >= 1) and (args.names[0] != 'github'):
            print('Invalid request. Must use "msl list" or "msl list github"')
        else:
            print_list(len(args.names) == 1, args.release_info)
    else:
        print('Invalid command "{}"'.format(args.command))

    sys.exit(0)
