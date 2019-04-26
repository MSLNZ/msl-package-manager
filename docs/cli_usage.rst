.. _cli-usage:

Command Line Interface
======================

Once the MSL Package Manager has been :ref:`installed <install>` you will be able to install,
uninstall, update, list and create MSL packages by using the command line interface.

*You can also directly call these functions through the* :ref:`API <pm-api-usage>`.

.. attention::
   Since MSL packages are part of a namespace_, uninstalling MSL packages using
   ``pip uninstall msl-<packaage name>`` will break the namespace_. Therefore, it is
   recommended to use ``msl uninstall <packaage name>`` to uninstall MSL packages.

.. _cache_note:
.. note::
   The information about the MSL repositories_ that are available on GitHub and the MSL packages_ on PyPI are
   cached for 24 hours after you request information about a repository or package. After 24 hours a subsequent
   request will automatically update the GitHub or PyPI cache. To force the cache to be updated immediately
   include the ``--update-cache`` flag.

To read the help documentation from the command line, run

.. code-block:: console

   msl --help

or, for help about a specific command (for example, the *install* command), run

.. code-block:: console

   msl install --help

.. _install_cli:

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

You can also use a wildcard, for example, to install all packages that start with ``pr-``:

.. code-block:: console

   msl install pr-*

.. _uninstall_cli:

uninstall
---------

Uninstall all MSL packages (except for the **msl-package-manager**):

.. code-block:: console

   msl uninstall --all

.. tip::
   You can also use ``remove`` as an alias for ``uninstall``, e.g., ``msl remove --all``

.. note::
   To uninstall the MSL Package Manager run ``pip uninstall msl-package-manager``.
   Use with caution. If you uninstall the MSL Package Manager and you still have
   other MSL packages installed then you may break the MSL namespace_.

Uninstall all MSL packages without asking for confirmation:

.. code-block:: console

   msl uninstall --all --yes

Uninstall a specific MSL package, for example **msl-loadlib** (you can ignore the **msl-** prefix):

.. code-block:: console

   msl uninstall loadlib

Uninstall multiple MSL packages:

.. code-block:: console

   msl uninstall loadlib equipment qt

.. _update_cli:

update
------

Update all MSL packages that are installed:

.. code-block:: console

   msl update --all

.. tip::
   You can also use ``upgrade`` as an alias for ``update``, e.g., ``msl upgrade --all``

Update all MSL packages without asking for confirmation:

.. code-block:: console

   msl update --all --yes

Update a specific MSL package, for example **msl-loadlib** (you can ignore the **msl-** prefix):

.. code-block:: console

   msl update loadlib

Update to a package that was released :ref:`\<24 hours ago <cache_note>`:

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

.. _list_cli:

list
----

List all MSL packages that are installed:

.. code-block:: console

   msl list

List all MSL repositories_ that are available on GitHub:

.. code-block:: console

   msl list --github

List all MSL packages_ that are available on PyPI:

.. code-block:: console

   msl list --pypi

Update the GitHub :ref:`cache <cache_note>` and then list all repositories_ that are available:

.. code-block:: console

   msl list --github --update-cache

Update the PyPI :ref:`cache <cache_note>` and then list all packages_ that are available:

.. code-block:: console

   msl list --pypi --update-cache

Show the information about the repositories_ (includes information about the branches and the tags)
in JSON_ format:

.. code-block:: console

   msl list --github --json

.. _create_cli:

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
directory) by specifying a value for the ``--dir`` argument and to automatically accept the default **author**
name and **email** address values by adding the ``--yes`` argument:

.. code-block:: console

   msl create MyPackage --yes --dir D:\create\package\here

To create a new package that is not part of the **MSL** namespace_, but, for example,
the Photometry and Radiometry namespace_ you can run,

.. code-block:: console

   msl create Monochromator --namespace pr

then to import the **PR-Monochromator** package you would use:

.. code-block:: pycon

   >>> from pr import monochromator

.. _authorize_cli:

authorize
---------

When requesting information about the MSL repositories_ that are available on GitHub there is a limit_ to
how often you can send requests to the GitHub API (this is the primary reason for :ref:`caching <cache_note>`
the information). If you have a GitHub account and include your username and password with each request then
this limit_ is increased. If you do not have a GitHub account then you could `sign up <github_signup_>`_ to
create an account.

By running this command you will be prompted for your GitHub username and password so that you send
authorized requests to GitHub.

.. code-block:: console

   msl authorize

.. important::
   Your GitHub username and password are saved in plain text in the file that is created. You should set
   the file permissions provided by your operating system to ensure that your GitHub credentials are safe.
   The file is saved to your ``$HOME`` directory.

.. _git: https://git-scm.com
.. _repositories: https://github.com/MSLNZ
.. _packages: https://pypi.org/search/?q=msl-
.. _namespace: https://packaging.python.org/guides/packaging-namespace-packages/
.. _limit: https://developer.github.com/v3/#rate-limiting
.. _github_signup: https://github.com/join?source=header-home
.. _JSON: https://www.json.org/
