API Examples
============

In cases where using the command-line interface is not desired, the following public functions are available:

* ``install(names, yes=False)`` -- to install MSL packages, names: list[str] or [] to install all packages
* ``uninstall(names, yes=False)`` -- to uninstall MSL packages, names: list[str] or [] to uninstall all packages
* ``create(names, author=None, email=None)`` -- to create new MSL package(s), names: str or list[str]
* ``get_github()`` -- returns a dictionary of MSL repositories that are available
* ``get_installed()`` -- returns a dictionary of MSL packages that are installed
* ``get_author()`` -- attempts to get the user's username (from their git_ account).
* ``get_email()`` -- attempts to get the user's email address (from their git_ account).

For example, to get a list of all MSL packages that are installed::

   >>> import msl.package_manager as pm
   >>> for pkg, info in pm.get_installed().items():
   ...     print(pkg, info)
   ...
   msl-package-manager ['(v0.1.0)', 'MSL Package Manager to install, uninstall, list and create MSL packages']
   msl-loadlib ['(v0.1.0)', 'Load a shared library']


.. _git: https://git-scm.com
