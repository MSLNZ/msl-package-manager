"""
Command line interface for the :ref:`create <create_cli>` command.
"""
from .utils import log
from .create import create
from .cli_argparse import add_argument_package_names
from .cli_argparse import add_argument_yes
from .cli_argparse import add_argument_quiet


HELP = 'Create a new MSL package.'

DESCRIPTION = HELP + """

To create a new MSL package you must specify the MSL package name,
and optionally the name and email address of the author and the path
to where you to want to save the package.
"""

EXAMPLE = """
Example:
  To create a new "MSL-MyPackage" template that contains the standard
  directory structure for a new MSL repository you should specify 
  "MyPackage" as shown by the following command:
  
  $ msl create MyPackage

  To set the values to use for the name and email address of the author:

  $ msl create MyPackage --author Firstname M. Lastname --email my.email@address.com

  To specify the path for where to save the package and to automatically accept the 
  default author name and email address, use:

  $ msl create MyPackage --yes --path /home/

  If you create a package called "MyPackage" then all the text in the 
  documentation will be displayed as "MSL-MyPackage"; however, to import the 
  package you would use:

  >>> from msl import mypackage
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
        '--path',
        help='The path to where to create the new package.\n'
             'If not specified then the new package will be created\n'
             'in the current working directory.'
    )
    add_argument_quiet(p)
    p.set_defaults(func=execute)


def execute(args, parser):
    """Executes the :ref:`create <create_cli>` command."""
    if args.names:
        create(*args.names, yes=args.yes, author=args.author, email=args.email, path=args.path)
    else:
        log.error('You must specify the name of the new package')
