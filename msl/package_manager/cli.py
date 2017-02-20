"""
Main entry point to either install, uninstall, list or create MSL packages
using the command-line interface.
"""
import argparse

from .install import install
from .uninstall import uninstall
from .create import create
from .list import show


def main():
    """
    Main entry point to either install, uninstall, list or create MSL packages
    using the command-line interface.
    """
    parser = argparse.ArgumentParser(description='Manage MSL packages')
    parser.add_argument('command', help='the command to run [install, uninstall, create, list]')
    parser.add_argument('names', help='the name(s) of the MSL package(s)', nargs='*')
    parser.add_argument('-a', '--author', nargs='+', help='the name of the author [create]')
    parser.add_argument('-e', '--email', help='the email address for the author [create]')
    parser.add_argument('-y', '--yes', action='store_true', help="Don't ask for confirmation to (un)install")
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
            show(len(args.names) == 1)
    else:
        raise ValueError('Invalid command "{}"'.format(args.command))
