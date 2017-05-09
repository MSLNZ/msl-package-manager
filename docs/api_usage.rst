.. _api_usage:

API Usage
=========

In cases where using the :ref:`command-line interface <cli-usage>` is not desired, you can use the :ref:`API <api>`
functions directly to install, uninstall, list and create MSL packages.

First, import the **MSL-Package-Manager**

.. code-block:: python

   >>> from msl import package_manager as pm

Print a list of all MSL packages that are installed

.. code-block:: python

   >>> pm.print_list()
   MSL Packages        Version Description
   ------------------- ------- ----------------------------------------------------------------------
   msl-loadlib         0.2.1   Load a shared library (and access a 32-bit library from 64-bit Python)
   msl-package-manager 1.0.0   Install, uninstall, update, list and create MSL packages

Print a list of all MSL repositories that are available (and include the version information)

.. code-block:: python

   >>> pm.print_list(True, True)
   MSL Repositories    Version Description
   ------------------- ------- ----------------------------------------------------------------------
   msl-loadlib         0.2.1   Load a shared library (and access a 32-bit library from 64-bit Python)
   msl-package-manager 0.1.0   Install, uninstall, update, list and create MSL packages

Get a dictionary of all the MSL packages that are installed

.. code-block:: python

   >>> pkg_dict = pm.helper.installed()
   >>> pkg_dict
   {'msl-loadlib': ['0.2.1', 'Load a shared library (and access a 32-bit library from 64-bit Python)'], 'msl-package-manager': ['1.0.0', 'Install, uninstall, update, list and create MSL packages']}
   >>> for pkg, info in pkg_dict.items():
   ...     print(pkg, info)
   ...
   msl-loadlib ['0.2.1', 'Load a shared library (and access a 32-bit library from 64-bit Python)']
   msl-package-manager ['1.0.0', 'Install, uninstall, update, list and create MSL packages']

Uninstall the **msl-loadlib** package

.. code-block:: python

   >>> pm.uninstall('loadlib')
   The following MSL packages will be UNINSTALLED:

     msl-loadlib: 0.2.1

   Proceed (y/[n])? n

Update the **msl-loadlib** package

.. code-block:: python

   >>> pm.update('loadlib')
   The following MSL packages will be UPDATED:

     msl-loadlib: 0.2.1 --> 0.3.0

   Continue (y/[n])? n
