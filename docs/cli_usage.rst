.. _cli-usage:

Command Line Interface
======================

Once the MSL Package Manager has been :ref:`installed <install>` you will be able to install, uninstall, update, list
and create MSL packages by using the command line interface.

*You can also directly call these functions through the* :ref:`API <api_usage>`.

The ``install``, ``uninstall``, ``update`` and ``list`` commands fetch data from MSL repositories_.
Some MSL packages are also available on PyPI_ and those packages can be installed by running
``pip install msl-<packaage name>`` and to show which packages are on PyPI_ by running ``pip search msl-``.
However, since MSL is a namespace_ package when doing a ``pip uninstall msl-<packaage name>`` you can
break the namespace_. Therefore, it is recommended to use ``msl uninstall <packaage name>`` to uninstall
MSL packages.

.. attention::
   The number of packages that are available on PyPI_ might be less than the number of repositories_ that
   are available on GitHub. Also the **master** branch of the repositories_ is where the latest stable
   version of the code is available and the releases on PyPI_ might not be the latest.

.. _github_cache_note:
.. note::
   The information about the MSL repositories_ that are available on GitHub are cached for 24 hours after you request
   information about a MSL repository. After 24 hours a subsequent request will automatically update the GitHub cache.
   Using a cache is meant to not exceed the `rate limit`_ from GitHub. To force the cache to be updated include the
   ``--update-github-cache`` argument.

To read the help documentation from the command line, type::

   msl --help

Or for help about a specific command::

   msl install --help

install
-------

Install all MSL packages that are available on the GitHub `repository <repositories_>`_::

   msl install --all

Install all MSL packages without asking for confirmation::

   msl install --all --yes

Install a specific MSL package, for example **msl-loadlib** (you can ignore the **msl-** prefix)::

   msl install loadlib

Install a package from a specific GitHub branch (by default the **master** branch is used)::

   msl install loadlib --branch develop

Install a package from a specific GitHub tag::

   msl install loadlib --tag v0.3.0

Install multiple MSL packages::

   msl install loadlib equipment qt

uninstall
---------

Uninstall all MSL packages (except for the **msl-package-manager**)::

   msl uninstall --all

.. tip::
   You can also use ``remove`` as an alias for ``uninstall``, e.g., ``msl remove --all``

.. note::
   To uninstall the MSL Package Manager run ``pip uninstall msl-package-manager``

Uninstall all MSL packages without asking for confirmation::

   msl uninstall --all --yes

Uninstall a specific MSL package, for example **msl-loadlib** (you can ignore the **msl-** prefix)::

   msl uninstall loadlib

Uninstall multiple MSL packages::

   msl uninstall loadlib equipment qt

update
------

Update all MSL packages (except for the **msl-package-manager**)::

   msl update --all

.. tip::
   You can also use ``upgrade`` as an alias for ``update``, e.g., ``msl upgrade --all``

.. note::
   To update the MSL Package Manager run ``pip install msl-package-manager --upgrade``

Update all MSL packages without asking for confirmation::

   msl update --all --yes

Update a specific MSL package, for example **msl-loadlib** (you can ignore the **msl-** prefix)::

   msl update loadlib

To ensure that you are updating to the latest :ref:`hot-off-the-press <github_cache_note>` release::

   msl update loadlib --update-github-cache

Update a package from a specific GitHub branch (by default the **master** branch is used)::

   msl update loadlib --branch develop

Update a package from a specific GitHub tag::

   msl update loadlib --tag v0.3.0

Update multiple MSL packages::

   msl update loadlib equipment qt

list
----

List all MSL packages that are installed::

   msl list

List all MSL repositories_ that are available to be installed::

   msl list --github

Update the GitHub cache and then list all MSL repositories_ that are available::

   msl list --github --update-github-cache

Print the detailed information about the repositories_::

   msl list --github --detailed

.. _create:

create
------

To create a new MSL package called **MyPackage**, run::

   msl create MyPackage

This will create a new folder (in the current working directory) called **msl-mypackage**. The name of the package
will be displayed as **MSL-MyPackage** in the documentation; however, when you want to import the package you would
use all lower-case letters, for example::

   >>> from msl import mypackage

Running the ``create`` command attempts to determine your user name and email address from your git_ account
to use as the **author** and **email** values in the files that it creates. You do not need git_ to be installed
to use the ``create`` command, but it helps to make the process more automated. Optionally, you can specify the
name to use for the **author** and the **email** address by passing additional arguments::

   msl create MyPackage --author Firstname Lastname --email my.email@address.com

You can also specify where to create the package (instead of the default location which is in the current working
directory) by specifying a value for the ``--path`` argument and to automatically accept the default **author**
name and **email** address values by adding the ``--yes`` argument::

   msl create MyPackage --yes --path D:\create\package\here

.. _git: https://git-scm.com
.. _repositories: https://github.com/MSLNZ
.. _rate limit: https://developer.github.com/v3/rate_limit/
.. _PyPI: https://pypi.org/search/?q=msl-
.. _namespace: https://packaging.python.org/guides/packaging-namespace-packages/
