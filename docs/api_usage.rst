.. _api_usage:

API Usage
=========

In cases where using the :ref:`command-line interface <cli-usage>` is not desired, you can use the :ref:`API <api>`
functions directly to install, uninstall, update, list and create MSL packages.

First, import the **MSL Package Manager**

.. code-block:: python

   >>> from msl import package_manager as pm

Print a list of all MSL packages that are installed

.. code-block:: python

   >>> pm.print_packages()
   MSL Package         Version Description
   ------------------- ------- ----------------------------------------------------------------------
   msl-loadlib         0.2.3   Load a shared library (and access a 32-bit library from 64-bit Python)
   msl-package-manager 1.3.0   Install, uninstall, update, list and create MSL packages

Print a list of all MSL repositories_ that are available

.. code-block:: python

   >>> pm.print_packages(from_github=True)
   MSL Repository      Version Description
   ------------------- ------- ----------------------------------------------------------------------
   msl-equipment       0.1.0   Manage and communicate with equipment in the laboratory
   msl-loadlib         0.2.3   Load a shared library (and access a 32-bit library from 64-bit Python)
   msl-package-manager 1.3.0   Install, uninstall, update, list and create MSL packages
   msl-qt              0.1.0   Custom Qt components for the user interface

Get a dictionary of all the MSL packages that are installed

.. code-block:: python

   >>> pkg_dict = pm.helper.installed()
   >>> for pkg, info in pkg_dict.items():
   ...     print(pkg, info)
   ...
   msl-loadlib {'version': '0.2.3', 'description': 'Load a shared library (and access a 32-bit library from 64-bit Python)'}
   msl-package-manager {'version': '1.3.0', 'description': 'Install, uninstall, update, list and create MSL packages'}

Install the **msl-equipment** and **msl-qt** packages

.. code-block:: python

   >>> pm.install(['equipment', 'qt'])
   The following MSL packages will be INSTALLED:

     msl-equipment: 0.1.0
     msl-qt: 0.1.0

   Proceed (y/[n])? y

Update the **msl-loadlib** package

.. code-block:: python

   >>> pm.update('loadlib')
   The following MSL packages will be UPDATED:

     msl-loadlib: 0.2.3 --> 0.3.1

   Proceed (y/[n])? y

Uninstall the **msl-loadlib** package

.. code-block:: python

   >>> pm.uninstall('loadlib')
   The following MSL packages will be REMOVED:

     msl-loadlib: 0.3.1

   Proceed (y/[n])? y

Create a new **MyPackage** package

.. code-block:: python

   >>> pm.create('MyPackage', author='my name', email='my@email.com', path='D:\\test')
   Created MSL-MyPackage in D:\test\msl-mypackage

.. _repositories: https://github.com/MSLNZ
