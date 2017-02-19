MSL Package Manager
===================

The MSL Package Manager allows you to install, uninstall, list and create MSL packages.

Install
=======

To install the MSL Package Manager run::

   $ pip install https://github.com/MSLNZ/msl-package-manager/archive/master.zip

Usage
=====

Once the MSL Package Manager has been installed you will be able to install, uninstall, list and create MSL packages
by using the command line interface.

Usage:install
=============

To ask before installing all MSL packages that are available at https://github.com/MSLNZ/, run::

   $ msl install

To install all MSL packages without asking for confirmation::

   $ msl install -y

To install a specific MSL package, for example **msl-loadlib** *(you can ignore the msl- prefix)*, run::

   $ msl install loadlib

To install multiple MSL packages, run::

   $ msl install loadlib instr

Usage:uninstall
===============

To ask before uninstalling all MSL packages (except for the **msl-package-manager**), run::

   $ msl uninstall

To uninstall all MSL packages without asking for confirmation (except for the **msl-package-manager**)::

   $ msl uninstall -y

To uninstall a specific MSL package, for example **msl-loadlib** *(you can ignore the msl- prefix)*, run::

   $ msl uninstall loadlib

To uninstall multiple MSL packages, run::

   $ msl uninstall loadlib instr

Usage:list
==========

To list all MSL packages that are installed, run::

   $ msl list

To list all MSL repositories that are available at https://github.com/MSLNZ/, run::

   $ msl list github

Usage:create
============

To create a new MSL package called **MyPackage**, run::

   $ cd path/where/you/want/to/create/the/package
   $ msl create MyPackage

This will create a new folder (in the current working directory) called **msl-mypackage**. The name of the package
will be displayed as **MSL-MyPackage** in the documentation; however, when you want to import the package you would
use all lower-case letters, for example::

   >>> from msl import mypackage

Running **msl create** will attempt to determine your user name and email address from your git_ account to use as the
**author** and **email** values in the files that it creates. Optionally, you can specify the name to use
for the **author** and the **email** address by passing additional command-line arguments::

   $ msl create MyPackage -a Firstname Lastname -e my.email@address.com

Developing with the newly-created package
-----------------------------------------

The newly-created package (that is created by running the above **msl create** command) contains two scripts
to help make development easier: **setup.py** and **test_envs.py**. *The following assumes that you are using*
conda_ *as your Python package manager.*

setup.py commands
+++++++++++++++++

The **setup.py** file (that is created from running **msl create**) can be run with various arguments in order to
perform unit tests, to create the documentation, and to distribute/install your MSL package.

*NOTE: The Python packages that are required to execute the following commands (e.g., the* pytest_, *and* sphinx_
*packages) are automatically installed (into the* **.eggs** *folder) if they are not already installed in your*
environment_. *Therefore, the first time that you run the* **docs** *or* **test** *command it will take
longer to finish executing the command because these packages (and their own dependencies) need to be downloaded
then installed. If you prefer to install these packages directly in your* environment_ *you can use*
``pip install -r requirements-dev.txt``

The following command will run all the tests that pytest_ finds in the **tests** folder as well as testing
all the example code that is located within the docstrings of the source code. A coverage_
report is created in the **htmlcov/index.html** file. This report provides an overview of which
classes/functions/methods are being tested and not tested::

   $ python setup.py test

Create the documentation files, which can be viewed by opening **docs/_build/html/index.html**::

   $ python setup.py docs

Automatically create the API documentation from the docstrings in the source code (uses
`sphinx-apidoc <http://www.sphinx-doc.org/en/stable/man/sphinx-apidoc.html>`_)::

   $ python setup.py apidoc

*NOTE: By default, the* **docs/_autosummary** *folder that is created by running this command is
automatically generated (overwrites existing files). As such, it is excluded from the repository (i.e., this folder is
specified in the* **.gitignore** *file). If you want to keep the files located in* **docs/_autosummary** *you should
rename the folder to, for example,* **docs/_api** *and then the changes made to the files in the* **docs/_api** *folder
will be kept and will be included in the repository.*

To display the help message::

   $ python setup.py --help

test_envs.py commands
+++++++++++++++++++++

Additionally, there is a **test_envs.py** file that is created from running **msl create**. tox_ and conda_ currently
do not "play nice" together, see
`here <https://bitbucket.org/hpk42/tox/issues/273/support-conda-envs-when-using-miniconda>`_ ,
and so this script provides a way around this issue. This script simulates tox_ by finding all conda
environment_\'s (ignores the **root** env) and runs the unit tests with each environment_.

Run the unit tests using all conda envs::

   $ python test_envs.py

Run the unit tests using all conda envs that include **py** in the env name::

   $ python test_envs.py -i py

Run the unit tests using all conda envs excluding those that contain **py26** and **py32** in the env name::

   $ python test_envs.py -e py26 py33

Show all the conda envs that are available and then exit::

   $ python test_envs.py --show

Show the conda envs that include **py** in the env name then exit::

   $ python test_envs.py --show -i py

Show the conda envs that include **py** in the env name *and* exclude those with **py33** in the name and then exit::

   $ python test_envs.py --show -i py -e py33


API
===

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

.. _pytest: http://doc.pytest.org/en/latest/
.. _sphinx: http://www.sphinx-doc.org/en/latest/#
.. _wheel: http://pythonwheels.com/
.. _coverage: http://coverage.readthedocs.io/en/latest/index.html
.. _git: https://git-scm.com
.. _environment: https://conda.io/docs/using/envs.html
.. _tox: https://tox.readthedocs.io/en/latest/
.. _conda: http://conda.readthedocs.io/en/latest/
