.. _pm-api-usage:

API Usage
=========

In cases where using the :ref:`command-line interface <cli-usage>` is not desired, you can use the :ref:`API <pm-api>`
functions directly to install, uninstall, update, list and create MSL packages.

First, import the **MSL Package Manager**

.. code-block:: pycon

   >>> from msl import package_manager as pm

Display the information about the MSL packages that are installed

.. code-block:: pycon

   >>> pm.info()
   MSL Package         Version Description
   ------------------- ------- ----------------------------------------------------------------------
   msl-loadlib         0.3.1   Load a shared library (and access a 32-bit library from 64-bit Python)
   msl-package-manager 1.4.0   Install, uninstall, update, list and create MSL packages

.. tip::
   You can set what information is displayed on the screen by changing the :py:ref:`levels`

   .. code-block:: pycon

      >>> import logging
      >>> pm.set_log_level(logging.INFO)

Display the information about the MSL repositories_ that are available

.. code-block:: pycon

   >>> pm.info(from_github=True)
   MSL Repository      Version Description
   ------------------- ------- ----------------------------------------------------------------------
   msl-equipment       0.1.0   Manage and communicate with equipment in the laboratory
   msl-loadlib         0.3.1   Load a shared library (and access a 32-bit library from 64-bit Python)
   msl-package-manager 1.4.0   Install, uninstall, update, list and create MSL packages
   msl-qt              0.1.0   Custom Qt components for the user interface

Get a dictionary of all MSL packages that are installed

.. code-block:: pycon

   >>> pkgs = pm.installed()
   >>> for pkg, info in pkgs.items():
   ...     print(pkg, info)
   ...
   msl-loadlib {'version': '0.3.1', 'description': 'Load a shared library (and access a 32-bit library from 64-bit Python)'}
   msl-package-manager {'version': '1.4.0', 'description': 'Install, uninstall, update, list and create MSL packages'}

Get a dictionary of all MSL repositories_ on GitHub

.. code-block:: pycon

   >>> pkgs = pm.github()
   >>> pkgs['msl-package-manager']
   {'description': 'Install, uninstall, update, list and create MSL packages', 'version': '1.4.0', 'tags': ['v1.4.0', 'v1.3.0', 'v1.2.0', 'v1.1.0', 'v1.0.3', 'v1.0.2', 'v1.0.1', 'v1.0.0', 'v0.1.0'], 'branches': ['develop', 'master']}

Get a dictionary of all MSL packages_ on PyPI

.. code-block:: pycon

   >>> pkgs = pm.pypi()
   >>> pkgs['msl-package-manager']
   {'description': 'Install, uninstall, update, list and create MSL packages', 'version': '1.4.0'}

Install the **msl-equipment** and **msl-qt** packages

.. code-block:: pycon

   >>> pm.install('equipment', 'qt')
   The following MSL packages will be INSTALLED:

     msl-equipment: 0.1.0
     msl-qt: 0.1.0

   Proceed ([y]/n)?

Update the **msl-loadlib** package

.. code-block:: pycon

   >>> pm.update('loadlib')
   The following MSL packages will be UPDATED:

     msl-loadlib: 0.3.1 --> 0.3.2

   Proceed ([y]/n)?

Uninstall the **msl-loadlib** package

.. code-block:: pycon

   >>> pm.uninstall('loadlib')
   The following MSL packages will be REMOVED:

     msl-loadlib: 0.3.1

   Proceed ([y]/n)?

Create a new **MSL-MyPackage** package

.. code-block:: pycon

   >>> pm.create('MyPackage', author='my name', email='my@email.com', path='D:\\create\\here')
   Created MSL-MyPackage in D:\create\here\msl-mypackage

.. _repositories: https://github.com/MSLNZ
.. _packages: https://pypi.org/search/?q=msl-
