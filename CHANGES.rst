=============
Release Notes
=============

Version 2.4.0.dev0
==================

- Added

  * the ``pip_options`` kwarg to the ``install``, ``update`` and ``uninstall`` functions
  * support for Python 3.8
  * can now create a new package that is not part of a namespace
  * ``authorise`` as an alias for ``authorize`` for the CLI
  * the ``--create``, ``--requires`` and ``--ini`` arguments to ``condatests.py``

- Changed

  * make the order of the log messages consistent: pypi -> github -> local
  * use a personal access token instead of a password for authentication to the GitHub API
    (authenticating to the GitHub API using a password is
    `deprecated <https://developer.github.com/v3/auth/#via-username-and-password>`_)
  * omit the `examples` directory from the coverage report and from pytest

- Fixed

  * call ``getpass.getuser()`` if git is installed but the `user.name` parameter has not been defined
  * do not split the text in the Description field to the next line in the middle of a word
    for the ``info()`` function
  * can now run ``condatests.py`` from any conda environment not just the `base` environment
  * check if an MSL package was installed via pip in `editable` mode
  * issue `#6 <https://github.com/MSLNZ/msl-package-manager/issues/6>`_ - add support for specifying
    a version number when installing/updating
  * issue `#5 <https://github.com/MSLNZ/msl-package-manager/issues/5>`_ - add support for
    specifying an extras_require value when installing/updating
  * issue `#4 <https://github.com/MSLNZ/msl-package-manager/issues/4>`_ - error updating a package if the
    installed name != repository name
  * the `tests_require` list in ``setup.py`` now specifies `zipp<2.0`, `pyparsing<3.0` and
    `pytest<5.0` for Python 2.7

- Removed

  * support for Python 3.4

Version 2.3.0 (2019.06.10)
==========================

- Added

  * ability to install, update, create and uninstall MSL packages that do not start with ``msl-``
  * the shorter ``-D`` flag for ``--disable-mslpm-version-check``
  * use of a shell-style wildcard when specifying the package name(s)
  * `authorize` as an API function

- Changed

  * renamed the optional ``--path`` argument to ``--dir`` in the `create` command
  * renamed the ``path`` kwarg to ``directory`` in the `create` method
  * renamed the ``-uc`` flag to ``-u`` for the ``--update-cache`` flag

- Fixed

  * running the ``list`` command did not align the Description text if the text continued on the next line
  * removed the ``--quiet`` flag in the `pip search msl-` query
  * removed the ``--process-dependency-links`` flag when installing packages
    (for compatibility with pip v19.0)

Version 2.2.0 (2019.01.06)
==========================

- Added

  * the ``--doctest-glob='*.rst'`` and ``doctest_optionflags = NORMALIZE_WHITESPACE`` options to the
    *setup.cfg* file that is generated when a new package is created
  * a ``--disable-mslpm-version-check`` flag
  * a ``-uc`` alias for ``--upgrade-cache``

- Changed

  * renamed ``test_envs.py`` to ``condatests.py`` and made it compatible with an optional *condatests.ini* file
  * disable pip from checking for version updates by using the ``--disable-pip-version-check`` flag
  * rename the ``--detailed`` flag to be ``--json``
  * moved the GitHub authorization file to the *.msl* directory and renamed the file to be *.mslpm-github-auth*

- Fixed

  * improved error handling if there is no internet connection
  * use ``threading.Thread`` instead of ``multiprocessing.pool.ThreadPool`` when fetching info from GitHub
    since using ``ThreadPool`` would cause some Python versions to hang (see https://bugs.python.org/issue34172)
  * colorama was not resetting properly

Version 2.1.0 (2018.08.24)
==========================

- Added

  * *autodoc_default_options* to conf.py for Sphinx 1.8 support
  * *nitpicky* to conf.py
  * the ``version_info`` named tuple now includes a *releaselevel*
  * can now update the MSL Package Manager using `msl update package-manager`
  * support for Python 3.7

- Removed

  * support for Python 3.3


Version 2.0.0 (2018.07.02)
==========================

- Added

  * ability to make authorized requests to the GitHub API (created ``authorize`` command)
  * create a 3x additive ``--quiet`` flag (for silencing WARNING, ERROR and CRITICAL logging levels)
  * show a message if the current version of the MSL Package Manager is not the latest release
  * ``.pytest_cache/`` and ``junk/`` directories are now in .gitignore

- Changed

  * use ``pkg_resources.working_set`` instead of ``pip.get_installed_distributions`` to get the information
    about the MSL packages that are installed
  * use logging instead of print statements
  * the function signature for ``install``, ``uninstall``, ``update`` and ``create``
  * replace ``--update-github-cache`` and ``--update-pypi-cache`` flags with a single ``--update-cache`` flag
  * rename function ``print_packages()`` to ``info()``
  * rename module ``helper.py`` to ``utils.py``
  * show the detailed info about the GitHub repos in JSON format
  * many changes to the documentation

- Fixed

  * ``ApiDocs`` in ``setup.py`` failed to run with Sphinx >1.7.0
  * bug if the GitHub repo does not contain text in the Description field
  * searching PyPI packages showed results that contained the letters ``msl`` but did not start with ``msl-``

- Removed

  * the constants ``IS_PYTHON2``, ``IS_PYTHON3`` and ``PKG_NAME``

Version 1.5.1 (2018.02.23)
==========================

- Fixed

  * the ``setup.py`` file is now compatible with Sphinx 1.7.0


Version 1.5.0 (2018.02.15)
==========================

- Added

  * the default install/update URI is PyPI (and uses the GitHub URI if the package does not exist on PyPI)
  * ``--update-pypi-cache`` and ``--pypi`` flags for the CLI

- Changed

  * default "yes/no" choice for the CLI was changed to be "yes"
  * ``test_envs.py`` has been updated to properly color the output text from pytest (v3.3.1) using colorama


Version 1.4.1 (2017.10.19)
==========================

- Added

  * ``pip`` as a dependency

- Changed

  * modified the template that is used for creating a new package:

    + the setup.py file is now self-contained, i.e., it no longer depends on other files to be available
    + removed requirements.txt and requirements-dev.txt so that one must specify the dependencies in install_requires
    + added the ApiDocs and BuildDocs classes from docs/docs_commands.py and removed docs/docs_commands.py

  * print the help message if no command-line argument was passed in
  * updated the documentation and the docstrings

Version 1.4.0 (2017.09.19)
==========================

- Added

  * add a ``--branch`` and ``--tag`` argument for the ``install`` and ``update`` commands
  * add a ``--path`` and ``--yes`` argument for the ``create`` command
  * added more functions to the helper module for the API:

    + check_msl_prefix
    + create_install_list
    + create_uninstall_list
    + get_zip_name
    + print_error
    + print_info
    + print_warning
    + print_install_uninstall_message
    + sort_packages

- Changed

  * the ``print_list`` function was renamed to ``print_packages``
  * updated the documentation and the docstrings

Version 1.3.0 (2017.08.31)
==========================

- Added

  * use a thread pool to request the version number of a release for MSL repositories on GitHub
  * cache the package information about the GitHub repositories
  * add an ``--update-github-cache`` flag for the CLI
  * update documentation and docstrings

- Fixed

  * the ``msl`` namespace got destroyed after uninstalling a package in Python 2.7
  * running ``python setup.py test`` now sets ``install_requires = []``
  * the ``test_envs.py`` file would hang if it had to "install eggs"

- Removed

  * the ``--release-info`` flag for the CLI is no longer supported

Version 1.2.0 (2017.08.10)
==========================
- add the ``--all`` flag for the CLI
- include ``--process-dependency-links`` argument for ``pip install``
- create **upgrade** alias for **update**
- bug fixes and edits for the print messages

Version 1.1.0 (2017.05.09)
==========================
- update email address to "measurement"
- previous release date (in CHANGES.rst) was yyyy.dd.mm should have been yyyy.mm.dd
- previous release should have incremented the minor number (new **update** feature)

Version 1.0.3 (2017.05.09)
==========================
- add **update** command
- run pip commands using sys.executable

Version 1.0.2 (2017.03.27)
==========================
- split requirements.txt using ``\n`` instead of by any white space
- remove unnecessary "import time"

Version 1.0.1 (2017.03.03)
==========================
- show help message if no package name was specified for "create" command
- remove unused 'timeout' argument from test_envs.py
- reorganize if-statement in "list" command to display "Invalid request" when appropriate

Version 1.0.0 (2017.03.02)
==========================
- separate **install**, **uninstall**, **create** and **list** functions into different modules
- fix MSL namespace
- edit test_envs.py to work with colorama and update stdout in real time
- add ``--yes`` and ``--release-info`` flags for CLI
- create documentation and unit tests
- many bug fixes

Version 0.1.0 (2017.02.19)
==========================
- initial release