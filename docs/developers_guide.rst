.. _pm-develop-guide:

====================
MSL Developers Guide
====================
This guide [#f1]_ shows you how to:

* :ref:`set-up`
* :ref:`commit-changes`
* :ref:`setup-and-condatests-scripts`
* :ref:`style-guide`

and describes *one way* to set up an environment to develop Python programs.
The guide does not intend to imply that the following is the *best way* to
develop programs in the Python language.

.. _set-up:

Install and set up Python, Git and PyCharm
------------------------------------------
This section uses the `MSL-LoadLib repository`_ as an example of a repository that one would like
to clone_ and import into `PyCharm <Community Edition of PyCharm_>`_.

The following instructions are written for a Windows x64 operating system. To install the same software on
a Debian architecture, such as `Ubuntu <https://www.ubuntu.com/>`_, run

.. code-block:: console

   sudo apt update
   sudo apt install git snapd
   sudo snap install pycharm-community --classic
   wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
   bash Miniconda*

and answer the questions that you are asked. After running these commands you can follow the appropriate
steps below.

.. attention::
   The screenshots below might not represent exactly what you see during the installation or configuration
   procedure as this depends on the version of the software that you are using.

1. Download a 64-bit version of Miniconda_.

2. Install Miniconda_. It is recommended to **Register** Anaconda but not to **Add** it to your PATH.

   .. image:: _static/anaconda_setup.png

3. Open the Anaconda Command Prompt

   .. image:: _static/anaconda_prompt.png

   and then enter the following command to update all Miniconda_ packages:

   .. code-block:: console

      conda update --all

4. It is usually best to create a new `virtual environment`_ for each Python project that you are working on to avoid
   possible conflicts between the packages that are required for each Python project or to test the code against
   different versions of Python (i.e., it solves the *Project X depends on version 1.x but Project Y depends on*
   *version 4.x* dilemma).

   In the Anaconda Command Prompt create a new ``py37`` `virtual environment`_ (you can pick another name, ``py37``
   is just an example of a name) and install the Python 3.7 interpreter in this environment *(NOTE: You can also*
   *create conda environment's from within PyCharm if you are not comfortable with the command line, see Step 9)*

   .. code-block:: console

      conda create --name py37 python=3.7

   You may also want to create another `virtual environment`_ so that you can run the code against another Python
   version. For example, here is an example of how to create a Python 2.7 `virtual environment`_ named ``py27``:

   .. code-block:: console

      conda create --name py27 python=2.7

5. Create a GitHub_ account *(if you do not already have one)*.

6. Download and install git_ *(accept the default settings)*. This program is used as the `version control system`_.

7. Download and install the `Community Edition of PyCharm`_ to use as an IDE_. This IDE_ is free to use and it provides
   a lot of the features that one expects from an IDE_. When asked to **Create associations** check the **.py** checkbox
   and you can also create a shortcut on the desktop *(you can accept the default settings for everything else that*
   *you are asked during the installation)*

   .. image:: _static/pycharm_installation1.png

8. Run PyCharm and perform the following:

   a) Import settings from a previous version of PyCharm *(if available)*

      .. image:: _static/pycharm_installation2.png

   b) Select the default editor theme *(you can also change the theme later)* and click
      **Skip Remaining and Set Defaults**

      .. image:: _static/pycharm_installation3.png

   c) Select the **Git** option from **Check out from Version Control**

      .. image:: _static/pycharm_github_checkout.png

   d) Click the **Log in to Github...** button

      .. image:: _static/pycharm_github_login1.png

      and then enter your GitHub_ account information *(see Step 5 above)* and click **Log In**

      .. image:: _static/pycharm_github_login2.png

   e) Clone_ the `MSL-LoadLib repository`_. Specify the **Directory** where you want to clone
      the repository *(NOTE: the* `MSL-LoadLib repository`_ *will only appear if you are part of the*
      MSLNZ_ *organisation on GitHub. A list of your own repositories will be available.)*

      .. image:: _static/pycharm_github_clone.png

   f) Open the `MSL-LoadLib repository`_ in PyCharm

      .. image:: _static/pycharm_github_open.png

9. Add the ``py37`` `virtual environment`_ that was created in Step 4 as the **Project Interpreter**
   *(NOTE: you can also create a new conda environment in Step 9d)*

   a) Press ``CTRL+ALT+S`` to open the **Settings** window

   b) Go to **Project Interpreter** and click on the *gear* button in the top-right corner

      .. image:: _static/pycharm_interpreter1.png

   c) Select **Add**

      .. image:: _static/pycharm_interpreter2.png

   d) Select **Conda Environment** :math:`\rightarrow` **Existing environment** and select the
      ``py37`` `virtual environment`_ that was created in Step 4 and then click **OK**
      *You can also create a new environment if you want*

      .. image:: _static/pycharm_interpreter3.png

   e) Click **Apply** then **OK**

   f) If you created a ``py27`` `virtual environment`_ then repeat Steps 9b-9d to add the
      Python 2.7 environment

10. The **MSL-LoadLib** project is now shown in the **Project** window and you can begin to modify the code.

.. _commit-changes:

Commit changes to a repository
------------------------------
The following is only a very basic example of how to upload changes to the source code to the
`MSL-LoadLib repository`_ by using PyCharm. See `this <githelp_>`_ link for a much more detailed overview
on how to use git.

.. note::
   This section assumes that you followed the instructions from :ref:`set-up`.

1. Make sure that the git Branch_ you are working on is up to date by performing a Pull_.

   a) Click on the blue, downward-arrow button in the top-right corner to update the project

      .. image:: _static/pycharm_github_pull_1.png

   b) Select the options for how you want to update the project *(the default options are usually okay)* and click
      **OK**

      .. image:: _static/pycharm_github_pull_2.png

2. Make changes to the code.

3. When you are happy with the changes that you have made you should Push_ the changes to the
   `MSL-LoadLib repository`_.

   a) Click on the green, check-mark button in the top-right corner to commit the changes

      .. image:: _static/pycharm_github_commit1.png

   b) Select the file(s) that you want to upload to the `MSL-LoadLib repository`_, add a useful message for the
      commit and then select **Commit and Push**.

      .. image:: _static/pycharm_github_commit2.png

   c) Finally, Push_ the changes to the `MSL-LoadLib repository`_.

      .. image:: _static/pycharm_github_commit3.png

.. _setup-and-condatests-scripts:

Use the setup.py and condatests.py scripts
------------------------------------------
MSL packages come with two scripts to help make development easier: :ref:`create-readme-setup` and
:ref:`create-readme-condatests`. See the :ref:`create-readme` page for an overview on how to use these scripts.

.. _style-guide:

Edit source code using the style guide
--------------------------------------
Please adhere to the following style guides when contributing to **MSL** packages. With multiple people contributing
to the code base it will be easier to understand if there is a coherent structure to how the code is written:

.. note::
   This section assumes that you followed the instructions from :ref:`set-up`.

* Follow the :pep:`8` style guide when possible *(by default, PyCharm will notify you if you do not)*.
* Docstrings must be provided for all public classes, methods and functions.
* For the docstrings use the `NumPy Style`_ format.

  * Press ``CTRL+ALT+S`` to open the **Settings** window and navigate to **Tools**
    :math:`\rightarrow` **Python Integrated Tools** to
    select the **NumPy** docstring format and then click **Apply** then **OK**.

    .. image:: _static/pycharm_numpy_style.png

* Do not use :func:`print` statements to notify the end-user of the status of a program. Use :mod:`logging` instead.
  This has the advantage that you can use different `logging levels`_ to decide what message types are displayed and
  which are filtered and you can also easily redirect all messages, for example, to a GUI widget or to a file. The
  `django project`_ has a nice overview on how to use Python's builtin logging module.

.. _Miniconda: https://docs.conda.io/en/latest/miniconda.html
.. _virtual environment: https://conda.io/docs/user-guide/tasks/manage-environments.html
.. _MSL-LoadLib repository: https://github.com/MSLNZ/msl-loadlib
.. _git: https://git-scm.com/downloads
.. _GitHub: https://github.com/join?source=header-home
.. _githelp: https://git-scm.com/doc
.. _version control system: https://en.wikipedia.org/wiki/Version_control
.. _Community Edition of PyCharm: https://www.jetbrains.com/pycharm/download/#section=windows
.. _IDE: https://en.wikipedia.org/wiki/Integrated_development_environment
.. _NumPy Style: https://numpydoc.readthedocs.io/en/latest/format.html#docstring-standard
.. _logging levels: https://docs.python.org/3/library/logging.html#logging-levels
.. _clone: https://git-scm.com/docs/git-clone
.. _Branch: https://git-scm.com/book/en/v2/Git-Branching-Branches-in-a-Nutshell
.. _Pull: https://git-scm.com/docs/git-pull
.. _Push: https://git-scm.com/docs/git-push
.. _django project: https://docs.djangoproject.com/en/3.0/topics/logging/
.. _MSLNZ: https://github.com/MSLNZ

.. [#f1] Software is identified in this guide in order to specify the installation and configuration procedure
   adequately. Such identification is not intended to imply recommendation or endorsement by the Measurement
   Standards Laboratory of New Zealand, nor is it intended to imply that the software identified are
   necessarily the best available for the purpose.
