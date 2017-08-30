"""
Main entry point to either install, uninstall, update, list or create MSL packages
using the command-line interface (CLI).
"""
import sys
import argparse

from colorama import Fore, Style

from .install import install
from .uninstall import uninstall
from .update import update
from .create import create
from .print_list import print_list


def main():
    """
    Main entry point to either install, uninstall, update, list or create MSL packages using the CLI.

    **This function should not be called directly as it is the main entry point for the CLI.**
    """
    parser = argparse.ArgumentParser(description='Manage MSL packages')

    parser.add_argument('command',
                        help="the command to run: 'install', 'uninstall', 'update', 'create' or 'list'")

    parser.add_argument('names',
                        help='the name(s) of the MSL package(s) to execute the command with', nargs='*')

    parser.add_argument('--all', action='store_true',
                        help="'(un)install' or 'update' all MSL packages")

    parser.add_argument('-y', '--yes', action='store_true',
                        help="don't ask for confirmation to '(un)install' or 'update' the MSL package(s)")

    parser.add_argument('-u', '--update-github-cache', action='store_true',
                        help="force the GitHub cache to be updated [used by 'install', 'update' and 'list']")

    parser.add_argument('-a', '--author', nargs='+',
                        help="the name of the author to use for the new package [used by 'create']")

    parser.add_argument('-e', '--email',
                        help="the email address of the author to use for the new package [used by 'create']")

    args = parser.parse_args()

    args.command = args.command.lower()

    if args.command in ('install', 'uninstall', 'update', 'upgrade') and len(args.names) == 0 and not args.all:
        msg = 'You must specify the MSL package name(s) to {} or use the "--all" flag'.format(args.command)
        print(Style.BRIGHT + Fore.RED + msg)

    elif args.command == 'install':
        install(args.names if args.names else 'ALL', args.yes, args.update_github_cache)

    elif args.command == 'uninstall':
        uninstall(args.names if args.names else 'ALL', args.yes)

    elif args.command == 'update' or args.command == 'upgrade':
        update(args.names if args.names else 'ALL', args.yes, args.update_github_cache)

    elif args.command == 'create':
        create(args.names, args.author, args.email)

    elif args.command == 'list':
        if len(args.names) == 0:
            print_list()
        elif len(args.names) == 1 and args.names[0].lower() == 'github':
            print_list(True, args.update_github_cache)
        else:
            print(Style.BRIGHT + Fore.RED + 'Invalid request. Must use "msl list" or "msl list github"')
    else:
        print(Style.BRIGHT + Fore.RED + 'Invalid command "{}"'.format(args.command))

    sys.exit(0)
