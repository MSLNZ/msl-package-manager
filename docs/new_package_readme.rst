.. _create-readme:

"Create" ReadMe
===============

An MSL package (that can be created by running the :ref:`msl create <create>` command) contains two scripts
to help make development easier: **setup.py** and **test_envs.py**. *The following assumes that you are using*
conda_ *as your Python package manager.*

setup.py commands
-----------------

The **setup.py** file (that is created by running :ref:`msl create <create>`) can be run with various arguments
in order to perform unit tests, to create the documentation, and to distribute/install your MSL package.

.. note::
   The Python packages that are required to execute the following commands (e.g., the pytest_, and sphinx_
   packages) are automatically installed (into the **.eggs** folder) if they are not already installed in your
   environment_. Therefore, the first time that you run the **docs** or **test** command it will take
   longer to finish executing the command because these packages (and their own dependencies) need to be downloaded
   then installed. If you prefer to install these packages directly in your environment_ you can use
   ``pip install -r requirements-dev.txt``.

The following command will run all the tests that pytest_ finds in the **tests** folder as well as testing
all the example code that is located within the docstrings of the source code. A coverage_
report is created in the **htmlcov/index.html** file. This report provides an overview of which
classes/functions/methods are being tested and not tested::

   python setup.py test

Create the documentation files, which can be viewed by opening **docs/_build/html/index.html**::

   python setup.py docs

Automatically create the API documentation from the docstrings in the source code (uses
`sphinx-apidoc <http://www.sphinx-doc.org/en/stable/man/sphinx-apidoc.html>`_)::

   python setup.py apidoc

.. note::
   By default, the **docs/_autosummary** folder that is created by running this command is automatically generated
   (overwrites existing files). As such, it is excluded from the repository (i.e., this folder is specified in the
   **.gitignore** file). If you want to keep the files located in **docs/_autosummary** you should rename the folder
   to, for example, **docs/_api** and then the changes made to the files in the **docs/_api** folder will be kept
   and will be included in the repository.

To display the help message::

   python setup.py --help

test_envs.py commands
---------------------

Additionally, there is a **test_envs.py** file that is created from running :ref:`msl create <create>`. At the time
of writing this script, tox_ and conda_ did not "play nice" together, see here_ , and so this script provided a way
around this issue. This script simulates tox_ by finding all conda environment_\'s (ignores the **root**
environment_) and runs the unit tests with each environment_.

Run the unit tests using all conda environment_\'s::

   python test_envs.py

Run the unit tests using all conda environment_\'s that include **py** in the environment_ name::

   python test_envs.py -i py

Run the unit tests using all conda environment_\'s excluding those that contain **py26** and **py32** in the
environment_ name::

   python test_envs.py -e py26 py33

Show all the conda environment_\'s that are available and then exit::

   python test_envs.py -s

Show the conda environment_\'s that include **py** in the environment_ name then exit::

   python test_envs.py -i py -s

Show the conda environment_\'s that include **py** in the environment_ name *and* exclude those with **py33** in the
name and then exit::

   python test_envs.py -i py -e py33 -s

.. _here: https://bitbucket.org/hpk42/tox/issues/273/support-conda-envs-when-using-miniconda
.. _pytest: http://doc.pytest.org/en/latest/
.. _sphinx: http://www.sphinx-doc.org/en/latest/#
.. _wheel: http://pythonwheels.com/
.. _coverage: http://coverage.readthedocs.io/en/latest/index.html
.. _git: https://git-scm.com
.. _environment: https://conda.io/docs/using/envs.html
.. _tox: https://tox.readthedocs.io/en/latest/
.. _conda: http://conda.readthedocs.io/en/latest/
