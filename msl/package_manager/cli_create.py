"""
Command line interface for the :ref:`create <create_cli>` command.
"""
from .utils import log
from .create import create
from .cli_argparse import add_argument_package_names
from .cli_argparse import add_argument_yes
from .cli_argparse import add_argument_quiet
from .cli_argparse import add_argument_disable_mslpm_version_check

HELP = 'Create a new MSL package.'

DESCRIPTION = HELP + """

To create a new MSL package you must specify the package name,
and optionally, the name and email address of the author, the
directory where you to want to save the package and the namespace
of the package.
"""

EXAMPLE = """
Example:
  To create a new "MSL-MyPackage" template that contains the standard
  directory structure for a new MSL repository you should specify 
  "MyPackage" as shown by the following command:
  
  $ msl create MyPackage

  To set the values to use for the name and email address of the author:

  $ msl create MyPackage --author Firstname M. Lastname --email my.email@address.com

  To specify the directory where to save the package and to automatically accept the 
  default author name and email address, use:

  $ msl create MyPackage --yes --dir /home/

  If you create a package called "MyPackage" then all the text in the 
  documentation will be displayed as "MSL-MyPackage"; however, to import the 
  package you would use:

  >>> from msl import mypackage

  To create a package that is not part of the MSL namespace, but instead it
  is part of the Photometry and Radiometry namespace, use:

  $ msl create Monochromator --namespace pr

  To import the "PR-Monochromator" package you would use:

  >>> from pr import monochromator

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
        help='The namespace that the package belongs to, for example\n'
             '"--namespace pr" will create a new package for the\n'
             'Photometry and Radiometry namespace. Default is "msl".'
    )
    add_argument_quiet(p)
    add_argument_disable_mslpm_version_check(p)
    p.set_defaults(func=execute)


def execute(args, parser):
    """Executes the :ref:`create <create_cli>` command."""
    if args.names:
        create(*args.names, yes=args.yes, author=args.author, email=args.email,
               directory=args.dir, namespace=args.namespace)
    else:
        log.error('You must specify the name of the new package')
