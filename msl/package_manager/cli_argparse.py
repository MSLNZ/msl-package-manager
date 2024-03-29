"""
Custom argument parsers.
"""
import argparse

from .utils import log


class ArgumentParser(argparse.ArgumentParser):

    def __init__(self, *args, **kwargs):
        """A custom argument parser."""
        kwargs['add_help'] = False  # use a custom help message (see below)
        kwargs['formatter_class'] = argparse.RawTextHelpFormatter
        super(ArgumentParser, self).__init__(*args, **kwargs)

        # so that capitalization and periods are consistent in the help
        self.add_argument(
            '-h', '--help',
            action='help',
            help='Show this help message and exit.',
            default=argparse.SUPPRESS
        )

    def get_command_name(self):
        """:class:`str`: Returns the name of the command, e.g., ``install``, ``list``, ..."""
        return self.prog.split()[-1]

    def contains_package_names(self, quiet=False):
        """Check whether package names were specified or the ``--all`` flag was used.

        .. versionchanged:: 2.5.0
           Added the `quiet` keyword argument.

        Parameters
        ----------
        quiet : :class:`bool`
            Whether to suppress the error message from being shown.

        Returns
        -------
        :class:`bool`
            Whether package names were specified or the ``--all`` flag was used.
        """
        args = self.parse_known_args()[0]
        if not args.all and not args.names:
            if not quiet:
                non_msl_flag = ''
                if args.cmd in ['update', 'upgrade']:
                    non_msl_flag = ' and/or the --non-msl flag'
                log.error('You must specify the MSL package name(s) to %s or use '
                          'the --all flag%s', args.cmd, non_msl_flag)
            return False
        return True


def add_argument_all(parser):
    """Add an ``--all`` argument to the parser."""
    parser.add_argument(
        '-a', '--all',
        action='store_true',
        default=False,
        help='{} all MSL packages.'.format(parser.get_command_name().capitalize()),
    )


def add_argument_branch(parser):
    """Add a ``--branch`` argument to the parser."""
    parser.add_argument(
        '-b', '--branch',
        help='The git branch to use to {} the package(s).'.format(parser.get_command_name()),
    )


def add_argument_package_names(parser):
    """Add a ``--names`` argument to the parser."""
    parser.add_argument(
        'names',
        nargs='*',
        help='The name(s) of the MSL package(s) to {}.\n'
             'The "msl-" prefix can be omitted (e.g., loadlib is\n'
             'equivalent to msl-loadlib). Also accepts shell-style\n'
             'wildcards (e.g., pr-*).'.format(parser.get_command_name())
    )


def add_argument_quiet(parser):
    """Add a ``--quiet`` argument to the parser."""
    parser.add_argument(
        '-q', '--quiet',
        action='count',
        default=0,
        help='Give less output. Option is additive, and can\n'
             'be used up to 4 times (which corresponds to\n'
             'silencing DEBUG, INFO, WARNING and ERROR\n'
             'logging levels).'
    )


def add_argument_tag(parser):
    """Add a ``--tag`` argument to the parser."""
    parser.add_argument(
        '-t', '--tag',
        help='The git tag to use to {} the package(s).'.format(parser.get_command_name()),
    )


def add_argument_update_cache(parser):
    """Add an ``--update-cache`` argument to the parser."""
    parser.add_argument(
        '-u', '--update-cache',
        action='store_true',
        default=False,
        help='Force the GitHub and PyPI caches to be updated.\n'
             'The information about MSL packages are cached\n'
             'for subsequent calls to the {} command. After 24\n'
             'hours the cache is automatically updated. Include\n'
             'this flag to force the cache to be updated now.'
             .format(parser.get_command_name()),
    )


def add_argument_yes(parser):
    """Add a ``--yes`` argument to the parser."""
    parser.add_argument(
        '-y', '--yes',
        action='store_true',
        default=False,
        help='Don\'t ask for confirmation to {} the package(s).'
             .format(parser.get_command_name()),
    )


def add_argument_disable_mslpm_version_check(parser):
    """Add a ``--disable-mslpm-version-check`` argument to the parser."""
    parser.add_argument(
        '-D', '--disable-mslpm-version-check',
        action='store_true',
        default=False,
        help='Don\'t check if there is a new version of the\n'
             'MSL-Package-Manager available.',
    )


def add_argument_commit(parser):
    """Add a ``--commit`` argument to the parser."""
    parser.add_argument(
        '-c', '--commit',
        help='The hash value of a git commit to use to {}\n'
             'a package.'.format(parser.get_command_name()),
    )
