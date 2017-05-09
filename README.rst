MSL Package Manager
===================

|docs|

The MSL Package Manager allows you to install, uninstall, list and create MSL packages.

Install
-------

To install the MSL Package Manager run::

   pip install https://github.com/MSLNZ/msl-package-manager/archive/master.zip

Documentation
-------------

The documentation for **MSL Package Manager** can be found `here <http://msl-package-manager.readthedocs.io/en/latest/?badge=latest>`_.

Usage
-----

Once the MSL Package Manager has been installed you will be able to install, uninstall, list and create MSL packages
by using the command line interface. *You can also directly access these classes from a script in addition to the CLI.*

install
+++++++

Install all MSL packages that are available (asks for confirmation before installing)::

   msl install

Install all MSL packages without asking for confirmation::

   msl install -y

Install a specific MSL package, for example **msl-loadlib** *(you can ignore the msl- prefix)*::

   msl install loadlib

Install the **msl-loadlib** package and display the latest release number::

   $ msl install loadlib -r

Install multiple MSL packages::

   msl install loadlib equipment

uninstall
+++++++++

Uninstall all MSL packages (except for the **msl-package-manager**)::

   msl uninstall

Uninstall all MSL packages (except for the **msl-package-manager**) without asking for confirmation::

   msl uninstall -y

Uninstall a specific MSL package, for example **msl-loadlib** *(you can ignore the msl- prefix)*::

   msl uninstall loadlib

Uninstall multiple MSL packages::

   msl uninstall loadlib equipment

update
------

Update all MSL packages (except for the **msl-package-manager**)::

   $ msl update

Update all MSL packages (except for the **msl-package-manager**) without asking for confirmation::

   $ msl update -y

Update a specific MSL package, for example **msl-loadlib** *(you can ignore the msl- prefix)*::

   $ msl update loadlib

Update multiple MSL packages::

   $ msl update loadlib equipment

list
++++

List all MSL packages that are installed::

   msl list

List all MSL repositories that are available at https://github.com/MSLNZ/ ::

   msl list github

Fetching the release information for each repository from GitHub will take longer than simply getting the names of
the repositories that are available. Therefore, the default action is to ignore the release information from GitHub.
Also, there is no guarantee that the owner of the repository created a release tag. If you want to include the
latest release version information in the printed list then use::

   msl list github -r

create
++++++

To create a new MSL package called **MyPackage**, run::

   cd path/where/you/want/to/create/the/package
   msl create MyPackage

This will create a new folder (in the current working directory) called **msl-mypackage**. The name of the package
will be displayed as **MSL-MyPackage** in the documentation; however, when you want to import the package you would
use all lower-case letters, for example::

   >>> from msl import mypackage

Running **msl create** will attempt to determine your user name and email address from your git_ account to use as the
**author** and **email** values in the files that it creates. Optionally, you can specify the name to use
for the **author** and the **email** address by passing additional command-line arguments::

   msl create MyPackage -a Firstname Lastname -e my.email@address.com


.. |docs| image:: https://readthedocs.org/projects/msl-package-manager/badge/?version=latest
   :target: http://msl-package-manager.readthedocs.io/en/latest/?badge=latest
   :alt: Documentation Status
   :scale: 100%

.. _git: https://git-scm.com
