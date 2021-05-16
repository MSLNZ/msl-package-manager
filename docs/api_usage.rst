.. _pm-api-usage:

API Usage
=========

In cases where using the :ref:`command-line interface <cli-usage>` is not desired, you can use the :ref:`API <pm-api>`
functions directly to install, uninstall, update, list and create MSL packages.

First, import the **MSL Package Manager**

.. code-block:: pycon

   >>> from msl import package_manager as pm

.. tip::
   You can set what information is displayed on the screen by changing the :py:ref:`levels`

   .. code-block:: pycon

      >>> import logging
      >>> pm.set_log_level(logging.INFO)

.. _install-api:

install
-------

:obj:`~msl.package_manager.install.install` the **msl-network** and **msl-qt** packages

.. code-block:: pycon

   >>> pm.install('network', 'qt')
   The following MSL packages will be INSTALLED:

   msl-network  0.5.0  [PyPI]
   msl-qt              [GitHub]

   Proceed ([y]/n)?

.. _uninstall-api:

uninstall
---------

:obj:`~msl.package_manager.uninstall.uninstall` the **msl-loadlib** package

.. code-block:: pycon

   >>> pm.uninstall('loadlib')
   The following MSL packages will be REMOVED:

     msl-loadlib  0.6.0

   Proceed ([y]/n)?

.. _update-api:

update
------

:obj:`~msl.package_manager.update.update` the **msl-loadlib** package

.. code-block:: pycon

   >>> pm.update('loadlib')
   The following MSL packages will be UPDATED:

     msl-loadlib  0.6.0 --> 0.7.0  [PyPI]

   Proceed ([y]/n)?

.. _list-api:

list
----

Display the information about the MSL packages that are installed, see :func:`~msl.package_manager.utils.info`

.. code-block:: pycon

   >>> pm.info()
       MSL Package     Version                           Description
   ------------------- ------- ----------------------------------------------------------------------
           msl-loadlib 0.6.0   Load a shared library (and access a 32-bit library from 64-bit Python)
   msl-package-manager 2.4.0   Install, uninstall, update, list and create MSL packages

Display the information about the MSL repositories_ that are available

.. code-block:: pycon

   >>> pm.info(from_github=True)
      MSL Repository   Version                           Description
   ------------------- ------- ----------------------------------------------------------------------
                   GTC 1.2.1   The GUM Tree Calculator for Python
        Quantity-Value 0.1.0   A package that supports physical quantity-correctness in Python code
         msl-equipment         Manage and communicate with equipment in the laboratory
                msl-io         Read and write data files
           msl-loadlib 0.7.0   Load a shared library (and access a 32-bit library from 64-bit Python)
           msl-network 0.5.0   Concurrent and asynchronous network I/O
   msl-package-manager 2.4.0   Install, uninstall, update, list and create MSL packages
                msl-qt         Custom Qt components for the user interface

Get a dictionary of all MSL packages that are :func:`~msl.package_manager.utils.installed`

.. code-block:: pycon

   >>> pkgs = pm.installed()
   >>> for pkg, info in pkgs.items():
   ...     print(pkg, info)
   ...
   msl-loadlib {'version': '0.6.0', 'description': 'Load a shared library (and access a 32-bit library from 64-bit Python)', 'repo_name': 'msl-loadlib'}
   msl-package-manager {'version': '2.4.0', 'description': 'Install, uninstall, update, list and create MSL packages', 'repo_name': 'msl-package-manager'}

Get a dictionary of all MSL repositories_ on GitHub, see :func:`~msl.package_manager.utils.github`

.. code-block:: pycon

   >>> pkgs = pm.github()
   >>> for key, value in pkgs['msl-package-manager'].items():
   ...     print('{}: {}'.format(key, value))
   ...
   description: Install, uninstall, update, list and create MSL packages
   version: 2.4.0
   tags: ['v2.4.0', 'v2.3.0', 'v2.2.0', 'v2.1.0', 'v2.0.0', 'v1.5.1', 'v1.5.0', 'v1.4.1', 'v1.4.0', 'v1.3.0', 'v1.2.0', 'v1.1.0', 'v1.0.3', 'v1.0.2', 'v1.0.1', 'v1.0.0', 'v0.1.0']
   branches: ['main']

Get a dictionary of all MSL packages_ on PyPI, see :func:`~msl.package_manager.utils.pypi`

.. code-block:: pycon

   >>> pkgs = pm.pypi()
   >>> pkgs['msl-package-manager']
   {'description': 'Install, uninstall, update, list and create MSL packages', 'version': '2.4.0'}

.. _create-api:

create
------

:obj:`~msl.package_manager.create.create` a new **MSL-MyPackage** package

.. code-block:: pycon

   >>> pm.create('MyPackage', author='my name', email='my@email.com', directory='D:/create/here')
   Created msl-MyPackage in 'D:/create/here\\msl-MyPackage'

.. _authorise-api:

authorise
---------

Create an authorisation file for the GitHub API, see :func:`~msl.package_manager.authorise.authorise`

.. code-block:: pycon

   >>> pm.authorise()
   Enter your GitHub username [default: ...]: >?
   Enter your GitHub personal access token: >?

.. _repositories: https://github.com/MSLNZ
.. _packages: https://pypi.org/search/?q=%22Measurement+Standards+Laboratory+of+New+Zealand%22
