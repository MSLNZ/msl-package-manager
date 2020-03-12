"""
Create a new package.
"""
import os
import time

from . import utils


def create(*names, **kwargs):
    """Create a new package.

    Parameters
    ----------
    *names
        The name(s) of the package(s) to create.
    **kwargs
        * author : :class:`str`
            The name of the author to use for the new package. If :data:`None` then uses
            :func:`.utils.get_username` to determine the author's name.
            Default is :data:`None`.
        * directory : :class:`str`
            The directory to create the new package(s) in. If :data:`None`
            then creates the new package(s) in the current working directory.
            Default is :data:`None`.
        * email : :class:`str`
            The author's email address. If :data:`None` then uses
            :func:`.utils.get_email` to determine the author's email address.
            Default is :data:`None`.
        * namespace : :class:`str`
            The namespace that the package belongs to. If `namespace` is :data:`None`
            or an empty string then create a new package that is not part of a namespace.
            Default is the ``'msl'`` namespace.
        * yes : :class:`bool`
            If :data:`True` then don't ask for verification for the `author` name
            and for the `email` address. This argument is only used if you do not
            specify the `author` or the `email` value. The verification step allows
            you to change the value that was automatically determined before the
            package is created. The default is to ask for verification before creating
            the package if the `author` or the `email` value was not specified.
            Default is :data:`False`.

    """
    # TODO Python 2.7 does not support named arguments after using *args
    #  we can define yes=False, author=None, email=None, directory=None in the
    #  function signature if we choose to drop support for Python 2.7
    utils._check_kwargs(kwargs, {'yes', 'author', 'email', 'directory', 'namespace'})

    yes = kwargs.get('yes', False)
    author = kwargs.get('author', None)
    email = kwargs.get('email', None)
    directory = kwargs.get('directory', None)
    namespace = kwargs.get('namespace', 'msl')
    if namespace:
        namespace = namespace.lower().replace('-', '')
    else:
        namespace = ''

    # ensure that the names contain valid characters for a python package
    # and that the folder does not already exist in the current working directory
    _names = [n.replace(' ', '_') for n in names]

    if directory is None:
        directory = os.getcwd()

    roots, pkg_names = [], []
    for name in _names:
        if namespace and name.lower().startswith(namespace + '-'):
            name = name[len(namespace)+1:]

        if name[0].isdigit():
            utils.log.warning('A package name cannot start with a number: ignored {!r}'.format(name))
            continue

        keep = True
        for c in name:
            if not (c.isalnum() or c == '_' or c == '-'):
                utils.log.warning('A package name can only contain letters, numbers and underscores: '
                                  'ignored {!r}'.format(name))
                keep = False
                break

        if keep:
            if namespace:
                basename = namespace + '-' + name
            else:
                basename = name
            root = os.path.join(directory, basename)
            if os.path.isdir(root):
                utils.log.warning('A {!r} folder already exists: ignored "{}"'.format(root, name))
            else:
                roots.append(root)
                pkg_names.append(name)

    if not pkg_names:
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
        author_name = utils.get_username()
        if not yes:
            try:
                new_name = utils._get_input('You can enter a new author name [default: {}]: '.format(author_name))
                if new_name:
                    author_name = new_name
            except:
                utils.log.error('Aborted -- cannot create MSL package')
                return

    # determine the author's email address
    if email is not None:
        if isinstance(email, str):
            email_address = email
        else:
            raise TypeError('The email address must be a string')
    else:
        email_address = utils.get_email()
        if not yes:
            try:
                new_email = utils._get_input('You can enter a new email address [default: {}]: '.format(email_address))
                if new_email:
                    email_address = new_email
            except:
                utils.log.error('Aborted -- cannot create MSL package')
                return

    # create the new package
    template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'template'))
    for msl_root, package in zip(roots, pkg_names):

        safe_pkg = package.replace('-', '_')

        aliases = {
            '${namespace}': namespace,
            '${package}': safe_pkg,
            '${namespace-or-package}': namespace if namespace else safe_pkg,
            '${full-name}': namespace + '-' + package if namespace else package,
            '${author}': author_name,
            '${year}': time.strftime('%Y'),
            '${email}': str(email_address),
            '${=}': '='*(len(os.path.basename(msl_root))),  # used to underline the header in a *.rst file
            '${sphinx-import}': 'from ' + namespace + ' import ' + safe_pkg if namespace else 'import ' + safe_pkg,
            '${installed-name}': namespace + '.' + safe_pkg if namespace else safe_pkg,
        }

        for root, dirs, files in os.walk(template_dir):
            if not namespace and '$' in root:
                # will create the source folder below
                continue

            new_dir = msl_root + root.split(template_dir)[1]
            new_dir = new_dir.replace('${namespace}', aliases['${namespace}'])
            new_dir = new_dir.replace('${package}', aliases['${package}'])
            if not os.path.isdir(new_dir):
                os.makedirs(new_dir)

            for filename in files:
                with open(os.path.join(root, filename), 'r') as fp:
                    lines = fp.read()

                if not namespace:
                    if filename == '.coveragerc':
                        lines = lines.replace('omit =\n', '')
                        lines = lines.replace('${namespace}/examples/*\n', '')
                    elif filename == 'setup.cfg':
                        lines = lines.replace('--ignore ${namespace}/examples\n', '')
                    elif filename == 'setup.py.template':
                        lines = lines.replace('${namespace}/${package}', safe_pkg)
                        lines = lines.replace('${namespace}*', safe_pkg)

                for alias in aliases:
                    lines = lines.replace(alias, aliases[alias])

                with open(os.path.join(new_dir, filename.replace('.template', '')), 'w') as fp:
                    fp.write(lines)

        if not namespace:
            # create the source folder
            src_dir = os.path.join(msl_root, package.replace('-', '_'))
            os.makedirs(src_dir)
            init = os.path.join(template_dir, '${namespace}', '${package}', '__init__.py.template')
            with open(init, 'r') as fp:
                lines = fp.read()
            for alias in aliases:
                lines = lines.replace(alias, aliases[alias])
            with open(os.path.join(src_dir, '__init__.py'), 'w') as fp:
                fp.write(lines)

        fullname = '{}-{}'.format(namespace, package) if namespace else package
        if os.path.isdir(msl_root):
            utils.log.info('Created {} in {!r}'.format(fullname, msl_root))
        else:
            utils.log.error('Error creating {!r}'.format(fullname))
