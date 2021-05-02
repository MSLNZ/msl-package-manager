.. _create-readme:

"create" ReadMe
===============

The MSL package that is created by running the :ref:`msl create <create-cli>` command contains two scripts
to help make development easier: :ref:`create-readme-setup` and :ref:`create-readme-condatests`.

.. _create-readme-setup:

setup.py
--------

The **setup.py** file (that is created by running :ref:`msl create <create-cli>`) includes additional commands
that can be used to run unit tests and to create the documentation for your MSL package.

.. note::
   The Python packages that are required to execute the following commands (e.g., pytest_ and sphinx_) are
   automatically installed (into the **.eggs** directory) if they are not already installed in your
   environment_. Therefore, the first time that you run the following commands it will take longer to finish
   executing the command because these packages (and their own dependencies) need to be downloaded then installed.
   If you prefer to install these packages directly into your environment_ you can run
   ``conda install pytest pytest-cov pytest-runner sphinx sphinx_rtd_theme``, or if you are using pip_ as
   your package manager then run ``pip install --editable .[docs,tests]`` from the directory where the
   **setup.py** file is located.

The following command will run all test modules that pytest_ finds as well as testing all the example code that is
located within the docstrings of the source code and in the **.rst** files in the **docs/** directory. To modify the
options that pytest_ will use to run the tests you can edit the **[tool:pytest]** section in **setup.cfg**.
A coverage_ report is created in the **htmlcov/index.html** file. This report provides an overview of which parts
of the code have been executed during the tests.

.. code-block:: console

   python setup.py tests

.. warning::

   pytest_ can only load one configuration file and uses the following search order to find that file:

      1. *pytest.ini* - used even if it does not contain a **[pytest]** section
      2. *tox.ini* - must contain a **[pytest]** section to be used
      3. *setup.cfg* - must contain a **[tool:pytest]** section to be used

   See the :ref:`condatests-ini` section for an example if you want to run pytest_ with custom options without
   modifying any of these configuration files.

Create the documentation files, uses sphinx-build_.
The documentation can be viewed by opening **docs/_build/html/index.html**

.. code-block:: console

   python setup.py docs

Automatically create the API documentation from the docstrings in the source code, uses
sphinx-apidoc_. The files are saved to
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

or

.. code-block:: console

   python setup.py --help-commands

.. _create-readme-condatests:

condatests.py
-------------

.. important::
   The following assumes that you are using conda_ as your environment_ manager.

Additionally, there is a **condatests.py** file that is created by running :ref:`msl create <create-cli>`. This
script will run the tests in all specified conda environment_\s. At the time of writing this script, tox_ and
conda_ were not compatible_ and so this script provided a way around this issue.

You can either pass options from the :ref:`condatests-cli` or by creating a :ref:`condatests-ini`.

.. _condatests-cli:

command line
++++++++++++

**condatests.py** accepts the following command-line arguments:

* ``--create`` - the Python version numbers to use to create conda environment_\s (e.g., 2 3.6 3.7.2)
* ``--include`` - the conda environment_\s to include (supports regex)
* ``--exclude`` - the conda environment_\s to exclude (supports regex)
* ``--requires`` - additional packages to install for the tests (can also be a path to a file_)
* ``--command`` - the command to execute with each conda environment_
* ``--ini`` - the path to a :ref:`condatests-ini`
* ``--list`` - list the conda environment_\s that will be used for the tests and then exit

You can view the help for **condatests.py** by running

.. code-block:: console

   python condatests.py --help

Run the tests with all conda environment_\'s using the ``python -m pytest`` command.
This assumes that a :ref:`condatests-ini` does not exist (which could change the default options).

.. code-block:: console

   python condatests.py

Run the tests with all conda environment_\s that include *py* in the environment_ name

.. code-block:: console

   python condatests.py --include py

Run the tests with all conda environment_\s but exclude those that contain *py26* and *py33* in the environment_ name

.. code-block:: console

   python condatests.py --exclude py26 py33

.. tip::

   Since a regex search is used to filter the environment_ names that follow the ``--exclude``
   (and also the ``--include``) option, the above command could be replaced with
   ``--exclude "py(26|33)"``. Surrounding the regex pattern with a ``"`` is necessary so that the
   *OR*, ``|``, regex symbol is not mistaken for a pipe_ symbol.

Run the tests with all conda environment_\s that include *dev* in the environment_ name but exclude
those with *dev33* in the environment_ name

.. code-block:: console

   python condatests.py --include dev --exclude dev33

Create new conda environment_\s for the specified Python versions (if the `minor` or `micro` version
numbers are not specified then the latest Python version that is available to conda will be installed).
After the test finishes the newly-created environment_ is removed. For example, the following
command will create environment_\s for the latest Python 2.x.x version, for the latest Python 3.6.x
version and for Python 3.7.4 and exclude all environment_\s that already exist

.. code-block:: console

   python condatests.py --create 2 3.6 3.7.4 --exclude .

You can also mix the ``--create``, ``--include`` and ``--exclude`` arguments

.. code-block:: console

   python condatests.py --create 3.7 --include dev --exclude dev33

Run the tests with all conda environment_\s using the command ``nosetests``

.. code-block:: console

   python condatests.py --command nosetests

Run the tests with all conda environment_\s using the command ``unittest discover -s tests/``

.. code-block:: console

   python condatests.py --command "unittest discover -s tests/"

Run the tests with all conda environment_\s using the command ``unittest discover -s tests/`` and ensure
that all the packages specified in a requirements file_ are installed in each environment_

.. code-block:: console

   python condatests.py --command "unittest discover -s tests/" --requires my_requirements.txt

List all conda environment_\s that will be used for the tests and then exit

.. code-block:: console

   python condatests.py --list

You can also use `--show` as an alias for `--list`

.. code-block:: console

   python condatests.py --show

List the conda environment_\s that include *dev* in the environment_ name and then exit

.. code-block:: console

   python condatests.py --include dev --list

Specify the path to a `condatests.ini <condatests-ini_>`_ file

.. code-block:: console

   python condatests.py --ini C:\Users\Me\my_condatests_config.ini

.. _condatests-ini:

configuration file
++++++++++++++++++

In addition to passing :ref:`condatests-cli` options, you can also save the options in an **condatests.ini**
configuration file. This is a standard ini-style configuration file with the options *create*, *include*,
*exclude*, *command* and *requires* specified under the **[envs]** section.

If a **condatests.ini** configuration file exists in the current working directory then it will
automatically be loaded by running

.. code-block:: console

   python condatests.py

Alternatively, you can also specify the path to the configuration file from the command line

.. code-block:: console

   python condatests.py --ini C:\Users\Me\my_condatests_config.ini

You can pass in command-line arguments as well as reading from the configuration file. The following
will load the **condatests.ini** file in the current working directory, print the conda environment_\s
that will be used for the tests and then exit

.. code-block:: console

   python condatests.py --show

Since every developer can name their environment_\s to be anything that they want, the **condatests.ini**
file is included in **.gitignore**.

The following are example **condatests.ini** files.

**Example 1**: Run ``python -m pytest`` (see :ref:`create-readme-setup`) with all conda environment_\s except
for the *base* environment_

.. code-block:: ini

   [envs]
   exclude=base

**Example 2**: Run ``python -m pytest`` with all conda environment_\s that include the text *py* in the name
of the environment_ but exclude the environment_\s that contain *py33* in the name (recall that a regex
search is used to filter the environment_ names)

.. code-block:: ini

   [envs]
   include=py
   exclude=py33

**Example 3**: Run ``python -m pytest`` only with newly-created conda environment_\s, exclude all
environment_\s that already exist and ensure that *scipy* is installed in each new environment_
(if the `minor` or `micro` version numbers of the Python environment_\s are not specified then the latest
Python version that is available to conda will be installed)

.. code-block:: ini

   [envs]
   create=2 3.5 3.6 3.7
   exclude=.
   requires=scipy

**Example 4**: Run ``python -m pytest`` with newly-created conda environment_\s and all conda environment_\s
that already exist that contain the text *dev* in the name of the environment_ except for the *dev33* environment_

.. code-block:: ini

   [envs]
   create=3.6 3.7.3 3.7.4
   include=dev
   exclude=dev33

**Example 5**: Run ``unittest``, for all modules in the **tests** directory, with all conda environment_\s
that include the text *dev* in the environment_ name

.. code-block:: ini

   [envs]
   include=dev
   command=unittest discover -s tests/

**Example 6**: Run pytest_ with customized options (i.e., ignoring any *pytest.ini*, *tox.ini* or *setup.cfg*
files that might exist) with the specified conda environment_\s.

.. code-block:: ini

   [envs]
   create=3.7
   include=dev27 myenvironment py36
   command=pytest -c condatests.ini

   [pytest]
   addopts =
      -x
     --verbose

.. note::

   The environment_ names specified in the *create*, *include*, *exclude* and *requires* option can
   be separated by a comma, by whitespace or both. So, ``include=py27,py36,py37``, ``include=py27 py36 py37``
   and ``include=py27, py36, py37`` are all equivalent.

.. _compatible: https://github.com/tox-dev/tox/issues/273
.. _pytest: https://doc.pytest.org/en/latest/
.. _sphinx: https://www.sphinx-doc.org/en/master/
.. _wheel: https://pythonwheels.com/
.. _coverage: https://coverage.readthedocs.io/en/latest/index.html
.. _git: https://git-scm.com
.. _environment: https://conda.io/docs/using/envs.html
.. _tox: https://tox.readthedocs.io/en/latest/
.. _conda: https://conda.readthedocs.io/en/latest/
.. _pipe: https://en.wikipedia.org/wiki/Pipeline_(Unix)
.. _file: https://docs.conda.io/projects/conda/en/latest/commands/install.html#Named%20Arguments
.. _pip: https://pip.pypa.io/en/stable/
.. _sphinx-apidoc: https://www.sphinx-doc.org/en/master/man/sphinx-apidoc.html
.. _sphinx-build: https://www.sphinx-doc.org/en/master/man/sphinx-build.html