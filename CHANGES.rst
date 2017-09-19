=============
Release Notes
=============

Version 1.4.1 (in development)
==============================


Version 1.4.0 (2017.09.19)
==========================
* Improvements

  - the implementation of the CLI got a complete overhaul (created an ArgumentParser subclass)
  - can now ``install`` or ``update`` from a branch or a tag from the MSL GitHub repositories
  - add a ``--branch`` and ``--tag`` argument for the ``install`` and ``update`` commands
  - add a ``--path`` and ``--yes`` argument for the ``create`` command
  - update the documentation and the docstrings
  - added more functions to the helper module for the API:
      + check_msl_prefix
      + create_install_list
      + create_uninstall_list
      + get_zip_name
      + print_error
      + print_info
      + print_warning
      + print_install_uninstall_message
      + sort_packages

* Changes

  - the ``print_list`` function was renamed to ``print_packages``

Version 1.3.0 (2017.08.31)
==========================
* Improvements

  - use a thread pool to request the version number of a release for MSL repositories on GitHub
  - cache the package information about the GitHub repositories
  - add an ``--update-github-cache`` flag for the CLI
  - update documentation and docstrings

* Bug Fixes

  - the ``msl`` namespace got destroyed after uninstalling a package in Python 2.7
  - running ``python setup.py test`` now sets ``install_requires = []``
  - the ``test_envs.py`` file would hang if it had to "install eggs"

* Removed

  - the ``--release-info`` flag for the CLI is no longer supported

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
- Initial release