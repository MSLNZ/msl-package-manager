"""
Create a new MSL package folder structure in the current working directory.
"""
import os
import time
from colorama import Fore, Style

from .helper import get_username, get_email, get_input

HELP_MSG = """\
To create a new MSL package you must specify an MSL package name,
and optionally the author name and email address.

For example, to create a new "MSL-MyPackage" template that contains the standard
directory structure for a new MSL repository you should specify MyPackage as
shown by the following command:

$ msl create MyPackage

To include the name of the author and an email address, use:

$ msl create MyPackage -a Firstname Lastname -e my.email@address.com

If you specify "MyPackage" then all the text in the documentation will be
displayed as "MSL-MyPackage"; however, to import the package you would use:

>>> from msl import mypackage
"""


def create(names, author=None, email=None):
    """
    Create a new MSL package folder structure in the current working directory.

    Args:
        names (str, list[str]): The name(s) of the MSL packages to create.

        author (str, optional): The name of the author. If :py:data:`None` then use
            :func:`~msl.package_manager.helper.get_author` to determine the author's name.

        email (str, optional): The author's email address. If :py:data:`None` then use
            :func:`~msl.package_manager.helper.get_email` to determine the author's email
            address.

    Raises:
        TypeError: If any of the input arguments do not have the correct data type
    """

    # ensure that the names contain valid characters for a python package
    # and that the folder does not already exist in the current working directory
    if isinstance(names, str):
        _names = [names.replace(' ', '_')]
    elif isinstance(names, (list, tuple)) and isinstance(names[0], str):
        if len(names) == 0:
            print(HELP_MSG)
            return
        _names = names[:]
    else:
        raise TypeError('The names argument must be either a string or a list of strings')

    roots, pkg_names = [], []
    for name in _names:
        if name[0].isdigit():
            print(Style.BRIGHT + Fore.YELLOW + 'A package name cannot start with a number -- ignored ' + name)
            continue

        keep = True
        for c in name:
            if not (c.isalnum() or c != '_'):
                print(Style.BRIGHT + Fore.CYAN + 'A package name can only contain letters, numbers and underscores -- ignored ' + name)
                keep = False
                break

        if keep:
            msl_name = 'msl-' + name.lower()
            root = os.path.join(os.getcwd(), msl_name)
            if os.path.isdir(root):
                print(Style.BRIGHT + Fore.MAGENTA + 'A {0} folder already exists. Will not overwrite'.format(msl_name))
            else:
                roots.append(root)
                pkg_names.append(name)

    if len(pkg_names) == 0:
        return

    # determine the author's name
    if author is not None:
        if isinstance(author, str):
            author_name = author
        elif isinstance(author, (list, tuple)):
            author_name = ' '.join(author)
        else:
            raise TypeError('The author\'s name must be either a string or a list of strings')
    else:
        author_name = get_username()
        try:
            new_name = get_input('You can enter a new author name [default: "{0}"]: '.format(author_name))
            if new_name:
                author_name = new_name
        except KeyboardInterrupt:
            print(Style.BRIGHT + Fore.RED + 'Aborted --  did not create MSL package.')
            return

    # determine the author's email address
    if email is not None:
        if isinstance(email, str):
            email_address = email
        else:
            raise TypeError('The email address must be a string')
    else:
        email_address = get_email()
        try:
            new_email = get_input('You can enter a new email address [default: "{0}"]: '.format(email_address))
            if new_email:
                email_address = new_email
        except KeyboardInterrupt:
            print(Style.BRIGHT + Fore.RED + 'Aborted --  did not create MSL package.')
            return

    # create the new package
    template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../template"))
    for msl_root, msl_pkg in zip(roots, pkg_names):

        aliases = {'${msl-package}': msl_pkg,
                   '${msl-package-lower}': msl_pkg.lower(),
                   '${author}': author_name,
                   '${year}': time.strftime('%Y'),
                   '${email}': email_address,
                   '${=}': '='*(len(os.path.basename(msl_root))),  # used to underline the header in a *.rst file
                   }

        for root, dirs, files in os.walk(template_dir):

            new_dir = msl_root + root.split(template_dir)[1]
            new_dir = new_dir.replace('${msl-package-lower}', aliases['${msl-package-lower}'])
            if not os.path.isdir(new_dir):
                os.makedirs(new_dir)

            for filename in files:
                with open(os.path.join(root, filename), 'r') as fp:
                    lines = fp.read()
                for alias in aliases:
                    lines = lines.replace(alias, aliases[alias])
                with open(os.path.join(new_dir, filename.replace('.template', '')), 'w') as fp:
                    fp.write(lines)

        if os.path.isdir(msl_root):
            print('Created MSL-' + msl_pkg)
        else:
            print(Style.BRIGHT + Fore.RED + 'Error creating... ' + msl_pkg)
