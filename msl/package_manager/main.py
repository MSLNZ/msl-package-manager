import os
import sys
import pip
import json
import time
import getpass
import argparse
import subprocess

from msl.package_manager import NAME

if sys.version_info.major == 2:
    from urllib2 import urlopen
elif sys.version_info.major == 3:
    from urllib.request import urlopen
else:
    raise NotImplementedError('Python major version is not 2 or 3')

__all__ = ['main', 'install', 'uninstall', 'create', 'get_github', 'get_installed', 'get_author', 'get_email']


def main(**kwargs):
    """
    Main entry point to either install, uninstall, list or create MSL packages.
    """
    if not kwargs:
        parser = argparse.ArgumentParser(description='Manage MSL packages')
        parser.add_argument('command', help='the command to run [install, uninstall, create, list]')
        parser.add_argument('names', help='the name(s) of the MSL package(s)', nargs='*')
        parser.add_argument('-a', '--author', nargs='+', help='the name of the author [create]')
        parser.add_argument('-e', '--email', help='the email address for the author [create]')
        args = parser.parse_args()
        command = args.command
        names = args.names
        author = args.author
        email = args.email
    else:
        command = kwargs['command']
        names = kwargs.get('names', [])
        author = kwargs.get('author', None)
        email = kwargs.get('email', None)

    if command == 'install':
        install(names)
    elif command == 'uninstall':
        uninstall(names)
    elif command == 'create':
        create(names, author, email)
    elif command == 'list':
        if len(names) >= 1 and (names[0] != 'github'):
            print('Invalid request. Must use "msl list" or "msl list github"')
            return

        if len(names) == 1:  # list github repositories
            header = ['MSL Repositories', 'Version', 'Description']
            pkgs = get_github()
        else:
            header = ['MSL Packages', 'Version', 'Description']
            pkgs = get_installed()

        # determine the maximum width of each column
        widths = [len(h) for h in header]
        for p in pkgs:
            widths = [max(widths[0], len(p)), max(widths[1], len(pkgs[p][0])), max(widths[1], len(pkgs[p][1]))]

        print(' '.join(header[i].ljust(widths[i]) for i in range(len(header))))
        print(' '.join('-'*w for w in widths))
        for p in pkgs:
            print(p.ljust(widths[0]) + ' ' + pkgs[p][0].ljust(widths[1]) + ' ' + pkgs[p][1].ljust(widths[2]))
    else:
        raise ValueError('Invalid command "{}"'.format(command))


def install(names=[]):
    """
    Use pip to install MSL packages from GitHub.

    Args:
        names (list[str]): A list of GitHub repository names. If an empty list then install all MSL packages.
    """
    for pkg in _get_packages('install', names):
        if pkg is not None:
            subprocess.call('pip install https://github.com/MSLNZ/{0}/archive/master.zip'.format(pkg))


def uninstall(names=[]):
    """
    Use pip to uninstall MSL packages from GitHub.

    Args:
        names (list[str]): A list of installed MSL packages. If an empty list then uninstall all MSL packages.
    """
    for pkg in _get_packages('uninstall', names):
        subprocess.call('pip uninstall -y ' + pkg)


def get_github():
    """
    Get the MSL repositories that are available on GitHub.

    Returns:
        A :py:class:`dict` with the repository name as key and the value is [version, description]
    """
    pkgs = {}
    try:
        repos = json.loads(urlopen('https://api.github.com/orgs/MSLNZ/repos').read().decode())
    except:
        # possible to get a "API rate limit exceeded for ..." if you call this too ofter
        return {None: ['unknown', 'cannot connect to GitHub right now...']}

    for repo in repos:
        if repo['name'].startswith('msl-'):
            latest_url = 'https://api.github.com/repos/MSLNZ/{}/releases/latest'.format(repo['name'])
            try:
                version = '({})'.format(json.loads(urlopen(latest_url, timeout=1).read().decode())['name'])
            except:
                version = 'unknown'
            pkgs[repo['name']] = [version, repo['description']]
    return pkgs


def get_installed():
    """
    Get the MSL packages that are installed.

    Returns:
        A :py:class:`dict` with the repository name as key and the value is [version, description]
    """
    pkgs = {}
    for pkg in pip.get_installed_distributions():
        if pkg.key.startswith('msl-'):
            description = 'unknown'
            for item in pkg._get_metadata(pkg.PKG_INFO):
                if 'Summary:' in item:
                    description = item.split('Summary:')[1].strip()
                    break
            pkgs[pkg.key] = ['(v' + pkg.version + ')', description]
    return pkgs


def _get_packages(_command, _names):
    """
    Gets the list of MSL packages, from either pip or GitHub.

    Returns:
        A :py:class:`dict` with the package name as keys and the package version as values.
    """
    pkgs = {}

    pkgs_installed = get_installed()

    names = []
    for name in _names:
        if name.startswith('msl-'):
            names.append(name)
        else:
            names.append('msl-' + name)

    if _command == 'install':
        pkgs_github = get_github()
        if len(names) == 0:
            names = [pkg for pkg in pkgs_github if pkg != NAME]

        for name in names:
            if name in pkgs_installed:
                print('The {0} package is already installed'.format(name))
            elif name not in pkgs_github:
                print('Cannot install {0} -- package not found'.format(name))
            else:
                pkgs[name] = pkgs_github[name]

    if _command == 'uninstall':
        if len(names) == 0:
            names = [pkg for pkg in pkgs_installed if pkg != NAME]

        for name in names:
            if name == NAME:
                print('Cannot uninstall {0} using itself. Use "pip uninstall {0}"'.format(NAME))
            elif name not in pkgs_installed:
                print('Cannot uninstall {0} -- package not found'.format(name))
            else:
                pkgs[name] = pkgs_installed[name]

    if pkgs:
        msg = 'The following MSL packages will be {0}ed:\n  '.format(_command)
        msg += '\n  '.join(pkg for pkg in pkgs)
        msg += '\nContinue (y/[n])? '

        res = get_input(msg).lower()
        if res != 'y':
            return {}
    else:
        print('No MSL packages to ' + _command)

    return pkgs


CREATE_MSG = """To create a new MSL package you must specify an MSL package name,
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
        names (str, list[str]): The name(s) of the MSL packages to create
        author (str, optional): If :py:data:`None` then the program attempts to read
            the author's name from the users git account.
        email (str, optional): If :py:data:`None` then the program attempts to read
            the email address from the users git account.
    """
    args = _parse_create_args(names, author, email)
    if args is None:
        return

    msl_roots, msl_pkgs, author, email = args

    for msl_root, msl_pkg in zip(msl_roots, msl_pkgs):

        aliases = {'${msl-package}': msl_pkg,
                   '${msl-package-lower}': msl_pkg.lower(),
                   '${author}': author,
                   '${year}': time.strftime('%Y'),
                   '${email}': email,
                   '${=}': '='*(len(os.path.basename(msl_root))),  # used to underline the header in a *.rst file
                   }

        template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../template"))
        for root, dirs, files in os.walk(template_dir):
            for filename in files:
                new_dir = msl_root + root.split(template_dir)[1]
                if new_dir.endswith('${msl-package-lower}'):
                    new_dir = new_dir.replace('${msl-package-lower}', aliases['${msl-package-lower}'])
                if not os.path.isdir(new_dir):
                    os.makedirs(new_dir)
                with open(os.path.join(root, filename), 'r') as fp:
                    lines = fp.read()
                for alias in aliases:
                    lines = lines.replace(alias, aliases[alias])
                with open(os.path.join(new_dir, filename.replace('.template', '')), 'w') as fp:
                    fp.write(lines)
        if os.path.isdir(msl_root):
            print('Created MSL-' + msl_pkg)
        else:
            print('ERROR creating... ' + msl_pkg)


def _parse_create_args(_names, _author, _email):
    """
    Parses the command line arguments to determine the:

    - name of the root directory
    - name of the package
    - authors name
    - authors email address

    Returns:
        A tuple -> (root, name, author, email)
    """
    if len(_names) == 0:
        print(CREATE_MSG)
        return

    names = []
    for name in _names:
        if name[0].isdigit():
            print('A package name cannot start with a number, ignored {0}'.format(name))
            continue

        keep = True
        for c in name:
            if not (c.isalnum() or c == '_'):
                print('A package name can only contain letters, numbers and underscores, ignored {0}'.format(name))
                keep = False
                break

        if keep:
            names.append(name)

    if len(names) == 0:
        return

    temp_names = names[:]
    roots = []
    names = []
    for name in temp_names:
        r = os.path.join(os.getcwd(), 'msl-' + name.lower())
        if os.path.isdir(r):
            print('A {0} folder already exists in the current working directory'.format('msl-' + name.lower()))
        else:
            roots.append(r)
            names.append(name)

    if len(roots) == 0:
        return

    if _author is not None:
        author = ' '.join(_author)
    else:
        author = get_author()
        try:
            value = get_input('You can enter a new author name [default: "{0}"]: '.format(author))
        except KeyboardInterrupt:
            return
        if value:
            author = value

    if _email is not None:
        email = _email
    else:
        email = get_email()
        try:
            value = get_input('You can enter a new email address [default: "{0}"]: '.format(email))
        except KeyboardInterrupt:
            return
        if value:
            email = value

    return roots, names, author, email


def get_author():
    """
    Returns the username for the current user.

    Firsts checks from git then from the OS if git is not installed.
    """
    try:
        p1 = subprocess.Popen(['git', 'config', 'user.name'], stdout=subprocess.PIPE)
        return p1.communicate()[0].decode().strip()
    except:
        return getpass.getuser()


def get_email():
    """
    Returns the email address for the git account.

    If git is not installed then returns a generic email address.
    """
    try:
        p2 = subprocess.Popen(['git', 'config', 'user.email'], stdout=subprocess.PIPE)
        return p2.communicate()[0].decode().strip()
    except:
        return 'unknown@email.com'


def get_input(msg):
    """
    Get user input for Python 2 and 3.
    """
    if sys.version_info.major == 2:
        return raw_input(msg)
    elif sys.version_info.major == 3:
        return input(msg)
    else:
        raise NotImplementedError('Python major version is not 2 or 3')
