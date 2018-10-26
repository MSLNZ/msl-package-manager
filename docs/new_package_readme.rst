.. _create_readme:

"create" ReadMe
===============

The MSL package that is created by running the :ref:`msl create <create_cli>` command contains two scripts
to help make development easier: :ref:`create_readme_setup` and :ref:`create_readme_envstest`.

.. _create_readme_setup:

setup.py
--------

The **setup.py** file (that is created by running :ref:`msl create <create_cli>`) includes additional commands
that can be used to run unit tests and to create the documentation for your MSL package.

.. note::
   The Python packages that are required to execute the following commands (e.g., pytest_ and sphinx_) are
   automatically installed (into the **.eggs** directory) if they are not already installed in your
   environment_. Therefore, the first time that you run the following commands it will take longer to finish
   executing the command because these packages (and their own dependencies) need to be downloaded then installed.
   If you prefer to install these packages directly into your environment_ you can run
   ``conda install pytest pytest-cov pytest-runner sphinx sphinx_rtd_theme``, or if you are not using conda_ as
   your package manager then replace ``conda`` with ``pip``.

The following command will run all test modules that pytest_ finds as well as testing all the example code that is
located within the docstrings of the source code. A coverage_ report is created in the **htmlcov/index.html** file.
This report provides an overview of which functions, classes, and methods are being tested and not tested.

.. code-block:: console

   python setup.py tests

Create the documentation files (uses `sphinx-build <https://www.sphinx-doc.org/en/latest/man/sphinx-build.html>`_),
which can be viewed by opening **docs/_build/html/index.html**

.. code-block:: console

   python setup.py docs

Automatically create the API documentation from the docstrings in the source code (uses
`sphinx-apidoc <https://www.sphinx-doc.org/en/stable/man/sphinx-apidoc.html>`_), which are saved to
**docs/_autosummary**

.. code-block:: console

   python setup.py apidocs

.. attention::
   By default, the **docs/_autosummary** directory that is created by running this command is automatically generated
   (overwrites existing files). As such, it is excluded from the repository (i.e., this directory is specified in the
   **.gitignore** file). If you want to keep the files located in **docs/_autosummary** you should rename the directory
   to, for example, **docs/_api** and then the changes made to the files in the **docs/_api** directory will be kept
   and can be included in the repository.

You can view additional help for **setup.py** by running

.. code-block:: console

   python setup.py --help

.. _create_readme_envstest:

envstest.py
-----------

.. important::
   The following assumes that you are using conda_ as your environment_ manager.

Additionally, there is a **envstest.py** file that is created by running :ref:`msl create <create_cli>`. This
script will run your tests in all specified conda environment_\s. At the time of writing this script, tox_ and
conda_ were not compatible_ and so this script provided a way around this issue.

You can either pass options from the :ref:`envstest-cli` or by creating a :ref:`envstest-ini`. If you do not specify
any command-line arguments to **envstest.py** then the configuration file will automatically be used; however, if no
configuration file exists then the tests will be run with the default settings, which are to run *setup.py test*
(see :ref:`create_readme_setup`) with all conda environment_\s.

.. _envstest-cli:

command line
++++++++++++

Run the tests with all conda environment_\'s using the *setup.py test* command (see :ref:`create_readme_setup`).
This assumes that a :ref:`envstest-ini` does not exist.

.. code-block:: console

   python envstest.py

Run the tests with all conda environment_\s that include "py" in the environment_ name

.. code-block:: console

   python envstest.py --include py

.. code-block:: console

   python envstest.py -i py

Run the tests with all conda environment_\s and exclude those that contain "py26" and "py33" in the environment_ name

.. code-block:: console

   python envstest.py --exclude py26 py33

.. code-block:: console

   python envstest.py -e py26 py33

.. tip::

   The environment_ names following the ``--include`` and ``--exclude`` arguments support regex. Therefore,
   the above command could be replaced with ``python envstest.py --exclude "py(26|33)"``. Using ``"``
   is necessary so that the *OR*, ``|``, regex symbol is not mistaken for a pipe_ symbol.

Run the tests with all conda environment_\s that include "dev" in the environment_ name and exclude those with
"dev33" in the environment_ name

.. code-block:: console

   python envstest.py --include dev --exclude dev33

Run the tests with all conda environment_\s using the command *pytest*

.. code-block:: console

   python envstest.py --command pytest

.. code-block:: console

   python envstest.py -c pytest

Run the tests with all conda environment_\s using the command *pytest --verbose*

.. code-block:: console

   python envstest.py --command "pytest --verbose"

List all conda environment_\s that are available and then exit

.. code-block:: console

   python envstest.py --list

.. code-block:: console

   python envstest.py -l

List the conda environment_\s that include "dev" in the environment_ name and then exit

.. code-block:: console

   python envstest.py --include dev --list

You can view the help for **envstest.py** by running

.. code-block:: console

   python envstest.py --help

.. _envstest-ini:

configuration file
++++++++++++++++++

To read the options to use when running the tests, instead of passing the options by the :ref:`envstest-cli`, create
a file called **envstest.ini** in the same directory as the **envstest.py** file and then run

.. code-block:: console

   python envstest.py

Since every developer who is running the tests can have different environment_\s available the **envstest.ini**
file is automatically included in the **.gitignore** file.

The following are example **envstest.ini** files.

**Example 1**: Run *pytest* with all conda environment_\s

.. code-block:: ini

   [envs]
   command=pytest

**Example 2**: Run *unittest*, for all modules in the **tests** directory, with all conda environment_\s
that include the text ``dev`` in the environment_ name

.. code-block:: ini

   [envs]
   include=dev
   command=unittest discover -s tests/

**Example 3**: Run *setup.py test* (see :ref:`create_readme_setup`) with all conda environment_\s that include the
text "py" in the name of the environment_ and exclude the environment_ that contains "py33" in the name

.. code-block:: ini

   [envs]
   include=py
   exclude=py33

**Example 4**: Run *pytest --verbose -x*  in the specified conda environment_\s

.. code-block:: ini

   [envs]
   include=dev27, myenvironment, py37
   command=pytest --verbose -x

.. _compatible: https://github.com/tox-dev/tox/issues/273
.. _pytest: https://doc.pytest.org/en/latest/
.. _sphinx: https://www.sphinx-doc.org/en/latest/#
.. _wheel: https://pythonwheels.com/
.. _coverage: https://coverage.readthedocs.io/en/latest/index.html
.. _git: https://git-scm.com
.. _environment: https://conda.io/docs/using/envs.html
.. _tox: https://tox.readthedocs.io/en/latest/
.. _conda: https://conda.readthedocs.io/en/latest/
.. _pipe: https://en.wikipedia.org/wiki/Pipeline_(Unix)
