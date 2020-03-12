"""
Command line interface for the :ref:`create <create_cli>` command.
"""
from .utils import log
from .create import create
from .cli_argparse import (
    add_argument_package_names,
    add_argument_yes,
    add_argument_quiet,
    add_argument_disable_mslpm_version_check,
)

HELP = 'Create a new package.'

DESCRIPTION = HELP + """

To create a new package you must specify the package name,
and optionally, the name and email address of the author, the
directory where you to want to save the package and the namespace
of the package.
"""

EXAMPLE = """
Example:
  To create a new package that is part of the msl namespace:
  
  $ msl create MyPackage

  To import the package, use:

  >>> from msl import MyPackage

  To create a package that is part of another namespace, use:

  $ msl create monochromator --namespace pr

  To import this package, use:

  >>> from pr import monochromator
  
  To create a package that is not part of a namespace, use:
  
  $ msl create mypackage --no-namespace
  
  To import this package, use:

  >>> import mypackage

"""


def add_parser_create(parser):
    """Add the :ref:`create <create_cli>` command to the parser."""
    p = parser.add_parser(
        'create',
        help=HELP,
        description=DESCRIPTION,
        epilog=EXAMPLE,
    )
    add_argument_package_names(p)
    add_argument_yes(p)
    p.add_argument(
        '-a', '--author',
        nargs='+',
        help='The name of the author to use for the new package.\n'
             'Can include spaces, for example: --author First Middle Last'
    )
    p.add_argument(
        '-e', '--email',
        help='The email address of the author to use for the new package.'
    )
    p.add_argument(
        '-d', '--dir',
        help='The directory to create the new package(s) in.\n'
             'If not specified then the package(s) will be created\n'
             'in the current working directory.'
    )
    p.add_argument(
        '-n', '--namespace',
        help='The namespace that the package belongs to. Default is "msl".'
    )
    p.add_argument(
        '--no-namespace',
        action='store_true',
        default=False,
        help='Do not create a namespace package.'
    )
    add_argument_quiet(p)
    add_argument_disable_mslpm_version_check(p)
    p.set_defaults(func=execute)


def execute(args, parser):
    """Executes the :ref:`create <create_cli>` command."""
    if args.names:
        if args.no_namespace:
            namespace = None
        elif args.namespace:
            namespace = args.namespace
        else:
            namespace = 'MSL'
        create(*args.names, yes=args.yes, author=args.author, email=args.email,
               directory=args.dir, namespace=namespace)
    else:
        log.error('You must specify the name of the new package')
