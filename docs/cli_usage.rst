.. _cli-usage:

Command Line Interface
======================

Once the MSL Package Manager has been :ref:`installed <install>` you will be able to install,
uninstall, update, list and create MSL packages by using the command line interface.

*You can also directly call these functions through the* :ref:`API <api_usage>`.

The ``install``, ``uninstall``, ``update`` and ``list`` commands fetch data from MSL repositories_.
Some MSL packages_ are also available on PyPI.

.. attention::
   Since MSL packages are part of a namespace_, uninstalling MSL packages using ``pip uninstall msl-<packaage name>``
   will break the namespace_. Therefore, it is recommended to use ``msl uninstall <packaage name>`` to
   uninstall MSL packages.

.. _cache_note:
.. note::
   The information about the MSL repositories_ that are available on GitHub and the MSL packages_ on PyPI are
   cached for 24 hours after you request information about a repository or package. After 24 hours a subsequent
   request will automatically update the GitHub or PyPI cache. To force the cache to be updated immediately
   include the ``--update-cache`` flag.

To read the help documentation from the command line, run:

.. code-block:: console

   msl --help

Or for help about a specific command:

.. code-block:: console

   msl install --help

install
-------

Install all MSL packages that are available on the GitHub `repository <repositories_>`_:

.. code-block:: console

   msl install --all

Install all MSL packages without asking for confirmation:

.. code-block:: console

   msl install --all --yes

Install a specific MSL package, for example **msl-loadlib** (you can ignore the **msl-** prefix):

.. code-block:: console

   msl install loadlib

Install a package from a specific GitHub branch (by default the **master** branch is used if the package
is not available on PyPI):

.. code-block:: console

   msl install loadlib --branch develop

Install a package from a specific GitHub tag:

.. code-block:: console

   msl install loadlib --tag v0.3.0

Install multiple MSL packages:

.. code-block:: console

   msl install loadlib equipment qt

uninstall
---------

Uninstall all MSL packages (except for the **msl-package-manager**):

.. code-block:: console

   msl uninstall --all

.. tip::
   You can also use ``remove`` as an alias for ``uninstall``, e.g., ``msl remove --all``

.. note::
   To uninstall the MSL Package Manager run ``pip uninstall msl-package-manager``

Uninstall all MSL packages without asking for confirmation:

.. code-block:: console

   msl uninstall --all --yes

Uninstall a specific MSL package, for example **msl-loadlib** (you can ignore the **msl-** prefix):

.. code-block:: console

   msl uninstall loadlib

Uninstall multiple MSL packages:

.. code-block:: console

   msl uninstall loadlib equipment qt

update
------

Update all MSL packages (except for the **msl-package-manager**):

.. code-block:: console

   msl update --all

.. tip::
   You can also use ``upgrade`` as an alias for ``update``, e.g., ``msl upgrade --all``

.. note::
   To update the MSL Package Manager run ``pip install -U msl-package-manager``

Update all MSL packages without asking for confirmation:

.. code-block:: console

   msl update --all --yes

Update a specific MSL package, for example **msl-loadlib** (you can ignore the **msl-** prefix):

.. code-block:: console

   msl update loadlib

Update a package that was released :ref:`\<24 hours ago <cache_note>`:

.. code-block:: console

   msl update loadlib --update-cache

Update a package from a specific GitHub branch (by default the **master** branch is used if the package
is not available on PyPI):

.. code-block:: console

   msl update loadlib --branch develop

Update a package from a specific GitHub tag:

.. code-block:: console

   msl update loadlib --tag v0.3.0

Update multiple MSL packages:

.. code-block:: console

   msl update loadlib equipment qt

list
----

List all MSL packages that are installed:

.. code-block:: console

   msl list

List all MSL repositories_ on GitHub that are available to be installed:

.. code-block:: console

   msl list --github

List all MSL packages_ on PyPI that are available to be installed:

.. code-block:: console

   msl list --pypi

Update the GitHub cache and then list all MSL repositories_ that are available:

.. code-block:: console

   msl list --github --update-cache

Print the detailed information about the branches and the tags for the repositories_:

.. code-block:: console

   msl list --github --detailed

.. _create:

create
------

To create a new MSL package called **MyPackage**, run:

.. code-block:: console

   msl create MyPackage

This will create a new folder (in the current working directory) called **msl-mypackage**. The name of the package
will be displayed as **MSL-MyPackage** in the documentation; however, when you want to import the package you would
use all lower-case letters, for example:

.. code-block:: pycon

   >>> from msl import mypackage

Running the ``create`` command attempts to determine your user name and email address from your git_ account
to use as the **author** and **email** values in the files that it creates. You do not need git_ to be installed
to use the ``create`` command, but it helps to make the process more automated. Optionally, you can specify the
name to use for the **author** and the **email** address by passing additional arguments:

.. code-block:: console

   msl create MyPackage --author Firstname Lastname --email my.email@address.com

You can also specify where to create the package (instead of the default location which is in the current working
directory) by specifying a value for the ``--path`` argument and to automatically accept the default **author**
name and **email** address values by adding the ``--yes`` argument:

.. code-block:: console

   msl create MyPackage --yes --path D:\create\package\here

.. _git: https://git-scm.com
.. _repositories: https://github.com/MSLNZ
.. _rate limit: https://developer.github.com/v3/rate_limit/
.. _packages: https://pypi.org/search/?q=msl-
.. _namespace: https://packaging.python.org/guides/packaging-namespace-packages/
