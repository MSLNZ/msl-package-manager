====================
MSL Developers Guide
====================
This guide shows you how to:

* `Install and set up Python, Git and PyCharm`_
* `Commit changes to a repository`_
* `Using the setup.py and test_envs.py scripts`_
* `Edit the source code using the style guide`_

This guide describes *one way* to set up a Python environment and it does not intend to imply that the following
is the *best way* to develop programs in the Python language [#f1]_.

.. _Install and set up Python, Git and PyCharm:

Install Python, Git and PyCharm
-------------------------------
This section uses the `MSL-LoadLib <repo_>`_ repository as an example of a repository that one would like
to clone_ and import into `PyCharm <Community Edition of PyCharm_>`_.

.. note::
   The following instructions are only valid for a Windows x64 operating system.

1. Download a 64-bit version of Miniconda_.

2. Install Miniconda_ in a folder of your choice, but make sure to **Add** and **Register** Anaconda.

   .. image:: _static/anaconda_setup.png

3. Open a `Windows Command Prompt`_ and update all Miniconda_ packages::

      conda update --yes --all

4. It is usually best to create a new `virtual environment`_ for each Python project that you are working on to avoid
   possible conflicts between the packages that are required for each Python project or to test the code against
   different versions of Python (i.e., it solves the "Project X depends on version 1.x but Project Y depends on
   version 4.x" dilemma).

   Create a new **msl** `virtual environment`_ (you can pick another name, **msl** is just an example of a name) and
   install the latest Python interpreter in this environment::

      conda create --yes --name msl python

   You may also want to create a new `virtual environment`_ so that you can test the code against another Python
   version. For example, here is an example of how to create a Python 2.7 `virtual environment`_::

      conda create --yes --name msl27 python=2.7

5. Create a GitHub_ account *(if you do not already have one)*.

6. Download and install git_ *(accept the default settings)*. This program is used as the `version control system`_.

7. Download and install the `Community Edition of PyCharm`_ to use as an IDE_. This IDE_ is free to use and it provides
   a lot of the features that one expects from an IDE_. When asked to **Create associations** check the **.py** checkbox
   *(you can accept the default settings for everything else that you are asked during the installation)*.

   .. image:: _static/pycharm_installation1.png

8. Run PyCharm and perform the following:

   a) Do not import settings from a previous version of PyCharm *(unless you have a settings file that you want to use)*.

      .. image:: _static/pycharm_installation2.png

   b) You can keep the default editor theme *(or select the one that you like; note: you can change the theme later)*.
    
      .. image:: _static/pycharm_installation3.png

   c) Select the **GitHub** option from **Check out from Version Control**.

      .. image:: _static/pycharm_github_checkout.png

   d) Enter your GitHub_ account information *(see step 5 above)* and click **Login**.

      .. image:: _static/pycharm_github_login.png

   e) Clone_ the **MSL-LoadLib** `repository <repo_>`_. You will have to change the path of the **Parent Directory**
      and you can choose the **Directory Name** to be any text that you want.

      .. image:: _static/pycharm_github_clone.png

   f) Open the `repository <repo_>`_ in PyCharm.

      .. image:: _static/pycharm_github_open.png

9. Specify the Python executable in the **msl** `virtual environment`_ as the **Project Interpreter**.
   
   a) Press **CTRL + ALT + S** to open the **Settings** window.
   
   b) Go to **Project Interpreter** and click on the *gear* button in the top-right corner.

      .. image:: _static/pycharm_interpreter1.png
   
   c) Select **Add Local**
    
      .. image:: _static/pycharm_interpreter2.png
      
   d) Navigate to the folder where the **msl** `virtual environment`_ is located (e.g., path\\to\\Miniconda\\envs\\msl),
      select the **python.exe** file and then click **OK**.
   
      .. image:: _static/pycharm_interpreter3.png

   e) Click **Apply** then **OK**.

   f) If you created a **msl27** `virtual environment`_ then repeat *step (d)* to add the Python 2.7 executable.

10. The **MSL-LoadLib** project is now shown in the **Project** window and you can begin to modify the code.

.. _Commit changes to a repository:

Commit changes to a repository
--------------------------------
The following is only a very basic example of how to upload changes to the source code to the `repository <repo_>`_
by using PyCharm. See `this link <githelp_>`_ for a much more detailed tutorial on how to use git.

.. note::
   This section assumes that you followed the instructions from `Install Python, Git and PyCharm`_.

1. Make sure that the git Branch_ you are working on is up to date by performing a Pull_.

   a) Click on the :abbr:`VCS (Version Control Software)` *downward-arrow button* in the top-right corner to
      update the project.

      .. image:: _static/pycharm_github_pull_1.png

   b) Select the options for how you want to update the project *(the default options are usually okay)* and click
      **OK**.

      .. image:: _static/pycharm_github_pull_2.png

2. Make changes to the code ...

3. When you are happy with the changes that you have made you should Push_ the changes to the `repository <repo_>`_.

   a) Click on the :abbr:`VCS (Version Control Software)` *upward-arrow button* in the top-right corner to
      commit the changes.
   
      .. image:: _static/pycharm_github_commit1.png

   b) Select the file(s) that you want to upload to the `repository <repo_>`_, add a useful message for the commit and
      then select **Commit and Push**.

      .. image:: _static/pycharm_github_commit2.png

   c) Finally, Push_ the changes to the `repository <repo_>`_.
   
      .. image:: _static/pycharm_github_commit3.png

.. _Using the setup.py and test_envs.py scripts:

Using the setup.py and test_envs.py scripts
-------------------------------------------

MSL packages come with two scripts to help make development easier: **setup.py** and **test_envs.py**. See the
:ref:`"Create" ReadMe <create-readme>` page for an overview on how to use these scripts.

.. _Edit the source code using the style guide:

Edit the source code using the style guide
------------------------------------------
Please adhere to the following style guides when contributing to **MSL** packages. With multiple people contributing
to the code base it will be easier to understand if there is a coherent structure to how code is written:

* Follow the :pep:`8` style guide when possible *(by default, PyCharm will notify you if you do not)*.
* Docstrings must be provided for all public classes, methods, and functions.
* For the docstrings use the `NumPy Style`_ format.

  * Press **CTRL + ALT + S** to open the **Settings** window and navigate to **Tools > Python Integrated Tools** to
    select the **NumPy** docstring format and then click **Apply** then **OK**.

    .. image:: _static/pycharm_numpy_style.png

* Do not use :func:`print` statements to notify the end-user of the status of a program. Use :mod:`logging` instead.
  This has the advantage that you can use different `logging levels`_ to decide what message types are displayed and
  which are filtered and you can also easily redirect all messages, for example, to a GUI widget or to a file. The
  `django project`_ has a nice overview of how to use Python's builtin logging module.

.. _Miniconda: http://conda.pydata.org/miniconda.html
.. _Windows Command Prompt: http://www.computerhope.com/issues/chusedos.htm
.. _virtual environment: http://conda.pydata.org/docs/using/envs.html
.. _repo: https://github.com/MSLNZ/msl-loadlib
.. _git: https://git-scm.com/downloads
.. _GitHub: https://github.com/join?source=header-home
.. _githelp: https://www.atlassian.com/git/tutorials/
.. _version control system: https://en.wikipedia.org/wiki/Version_control
.. _Community Edition of PyCharm: https://www.jetbrains.com/pycharm/download/#section=windows
.. _IDE: https://en.wikipedia.org/wiki/Integrated_development_environment
.. _pytest: http://doc.pytest.org/en/latest/
.. _sphinx: http://www.sphinx-doc.org/en/latest/#
.. _sphinx-apidoc: http://www.sphinx-doc.org/en/stable/man/sphinx-apidoc.html
.. _wheel: http://pythonwheels.com/
.. _coverage: http://coverage.readthedocs.io/en/latest/index.html
.. _build_sphinx: http://www.sphinx-doc.org/en/latest/invocation.html#invocation-of-sphinx-build
.. _Google Style: http://www.sphinx-doc.org/en/latest/ext/example_google.html
.. _NumPy Style: https://github.com/numpy/numpy/blob/master/doc/HOWTO_DOCUMENT.rst.txt
.. _logging levels: https://docs.python.org/3/library/logging.html#logging-levels
.. _clone: https://git-scm.com/docs/git-clone
.. _Branch: https://git-scm.com/book/en/v2/Git-Branching-Branches-in-a-Nutshell
.. _Pull: https://git-scm.com/docs/git-pull
.. _Push: https://git-scm.com/docs/git-push
.. _django project: https://docs.djangoproject.com/en/1.10/topics/logging/

.. [#f1] Software is identified in this guide in order to specify the installation and configuration procedure
         adequately. Such identification is not intended to imply recommendation or endorsement by the Measurement
         Standards Laboratory of New Zealand, nor is it intended to imply that the software identified are
         necessarily the best available for the purpose.
