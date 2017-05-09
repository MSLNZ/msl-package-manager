.. _api:

=============================
MSL-LoadLib API Documentation
=============================

The root package is

.. autosummary::

    msl.package_manager

which has the following classes

+----------------------------------------------+-------------------------------------------------------------+
| :class:`msl.package_manager.create           | Create a new MSL package in the current working directory.  |
| <msl.package_manager.create.create>`         |                                                             |
+----------------------------------------------+-------------------------------------------------------------+
| :class:`msl.package_manager.print_list       | Print the list of MSL packages that are available.          |
| <msl.package_manager.print_list.print_list>` |                                                             |
+----------------------------------------------+-------------------------------------------------------------+
| :class:`msl.package_manager.install          | Use pip to install MSL repositories from GitHub.            |
| <msl.package_manager.install.install>`       |                                                             |
+----------------------------------------------+-------------------------------------------------------------+
| :class:`msl.package_manager.uninstall        | Use pip to uninstall MSL packages.                          |
| <msl.package_manager.uninstall.uninstall>`   |                                                             |
+----------------------------------------------+-------------------------------------------------------------+
| :class:`msl.package_manager.update           | Use pip to update MSL packages.                             |
| <msl.package_manager.update.update>`         |                                                             |
+----------------------------------------------+-------------------------------------------------------------+

and the following helper module

+----------------------------------------------+-------------------------------------------------------------------+
| :mod:`msl.package_manager.helper`            | Helper functions for the MSL Package Manager.                     |
+----------------------------------------------+-------------------------------------------------------------------+

Package Structure
-----------------

.. toctree::

   msl.package_manager <_api/msl.package_manager>
   msl.package_manager.cli <_api/msl.package_manager.cli>
   msl.package_manager.create <_api/msl.package_manager.create>
   msl.package_manager.helper <_api/msl.package_manager.helper>
   msl.package_manager.install <_api/msl.package_manager.install>
   msl.package_manager.print_list <_api/msl.package_manager.print_list>
   msl.package_manager.uninstall <_api/msl.package_manager.uninstall>
   msl.package_manager.update <_api/msl.package_manager.update>
