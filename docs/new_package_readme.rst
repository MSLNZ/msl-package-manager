.. _create_readme:

"create" ReadMe
===============

The MSL package that is created by running the :ref:`msl create <create_cli>` command contains two scripts
to help make development easier: :ref:`create_readme_setup` and :ref:`create_readme_condatests`.

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
located within the docstrings of the source code. To modify the options that pytest_ will use to run the tests you
can edit the **[tool:pytest]** section in **setup.cfg**. A coverage_ report is created in the **htmlcov/index.html**
file. This report provides an overview of which parts of the code have been executed during the tests.

.. code-block:: console

   python setup.py tests

.. warning::

   pytest_ can only load one configuration file and uses the following search order to find that file:

      1. *pytest.ini* - used even if it does not contain a **[pytest]** section
      2. *tox.ini* - must contain a **[pytest]** section to be used
      3. *setup.cfg* - must contain a **[tool:pytest]** section to be used

   See the :ref:`condatests-ini` section for an example if you want to run pytest_ with custom options without
   modifying any of these configuration files.

Create the documentation files, uses `sphinx-build <https://www.sphinx-doc.org/en/latest/man/sphinx-build.html>`_,
which can be viewed by opening **docs/_build/html/index.html**

.. code-block:: console

   python setup.py docs

Automatically create the API documentation from the docstrings in the source code, uses
`sphinx-apidoc <https://www.sphinx-doc.org/en/stable/man/sphinx-apidoc.html>`_, which are saved to
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

.. _create_readme_condatests:

condatests.py
-------------

.. important::
   The following assumes that you are using conda_ as your environment_ manager.

Additionally, there is a **condatests.py** file that is created by running :ref:`msl create <create_cli>`. This
script will run your tests in all specified conda environment_\s. At the time of writing this script, tox_ and
conda_ were not compatible_ and so this script provided a way around this issue.

You can either pass options from the :ref:`condatests-cli` or by creating a :ref:`condatests-ini`. If you do not specify
any command-line arguments to **condatests.py** then the configuration file will automatically be used; however, if no
configuration file exists then the tests will be run with the default settings, which are to run ``setup.py tests``
(see :ref:`create_readme_setup`) with all conda environment_\s.

.. note::

   A regex search is performed when filtering environment_ names for the ``--include`` and ``--exclude`` options.

.. _condatests-cli:

command line
++++++++++++

Run the tests with all conda environment_\'s using the ``setup.py tests`` command (see :ref:`create_readme_setup`).
This assumes that a :ref:`condatests-ini` does not exist (which could change the default options).

.. code-block:: console

   python condatests.py

Run the tests with all conda environment_\s that include "py" in the environment_ name

.. code-block:: console

   python condatests.py --include py

.. code-block:: console

   python condatests.py -i py

Run the tests with all conda environment_\s and exclude those that contain "py26" and "py33" in the environment_ name

.. code-block:: console

   python condatests.py --exclude py26 py33

.. code-block:: console

   python condatests.py -x py26 py33

.. tip::

   Since a regex search is used to filter the environment_ names that follow the ``--exclude``
   (and also the ``--include``) option, the above command could be replaced with
   ``--exclude "py(26|33)"``. Surrounding the regex pattern with a ``"`` is necessary so that the
   *OR*, ``|``, regex symbol is not mistaken for a pipe_ symbol.

Run the tests with all conda environment_\s that include "dev" in the environment_ name and exclude
those with "dev33" in the environment_ name

.. code-block:: console

   python condatests.py --include dev --exclude dev33

Run the tests with all conda environment_\s using the command ``nosetests``

.. code-block:: console

   python condatests.py --command nosetests

.. code-block:: console

   python condatests.py --c nosetests

Run the tests with all conda environment_\s using the command ``unittest discover -s tests/``

.. code-block:: console

   python condatests.py --command "unittest discover -s tests/"

List all conda environment_\s that are available and then exit

.. code-block:: console

   python condatests.py --list

.. code-block:: console

   python condatests.py -l

List the conda environment_\s that include "dev" in the environment_ name and then exit

.. code-block:: console

   python condatests.py --include dev --list

You can view the help for **condatests.py** by running

.. code-block:: console

   python condatests.py --help

.. _condatests-ini:

configuration file
++++++++++++++++++

In addition to passing :ref:`condatests-cli` options, you can also save the options in an **condatests.ini**
configuration file, which must be saved to the same directory as the **condatests.py** file. This is a standard
ini-style configuration file with the options (e.g., *include*, *exclude*, *command*) specified under the
**[envs]** section. This configuration file is loaded when the following command is executed

.. code-block:: console

   python condatests.py

Since every developer can name their environment_\s to be anything that they want the **condatests.ini**
file is included in **.gitignore**.

The following are example **condatests.ini** files.

**Example 1**: Run the tests with all conda environment_\s except for the "base" environment_

.. code-block:: ini

   [envs]
   exclude=base

**Example 2**: Run the tests with all conda environment_\s that include the text "py" in the name of the environment_
and exclude the environment_\s that contain "py33" in the name (recall that a regex search is used to filter the
environment_ names)

.. code-block:: ini

   [envs]
   include=py
   exclude=py33

**Example 3**: Run ``unittest``, for all modules in the **tests** directory, with all conda environment_\s
that include the text "dev" in the environment_ name

.. code-block:: ini

   [envs]
   include=dev
   command=unittest discover -s tests/

**Example 4**: Run pytest_ with customized options (i.e., ignoring any *pytest.ini*, *tox.ini* or *setup.cfg*
files that might exist) with the specified conda environment_\s.

.. code-block:: ini

   [envs]
   include=dev27, myenvironment, py37
   command=pytest -c condatests.ini

   [pytest]
   addopts =
      -x
     --verbose

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
