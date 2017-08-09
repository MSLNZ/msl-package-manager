=============
Release Notes
=============

Version 1.1.1 (in development)
==============================
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