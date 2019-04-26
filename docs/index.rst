.. _msl-package-manager-welcome:

MSL Package Manager
===================

The **MSL Package Manager** allows you to install, uninstall, update, list and create packages
that are used at the `Measurement Standards Laboratory of New Zealand`_.

All MSL packages that start with ``msl-`` are part of the **msl** namespace_. This allows one to
split sub-packages and modules across multiple, separate distribution packages while still
maintaining a single, unifying package structure.

All MSL packages are available as GitHub repositories_ and some have been published as PyPI packages_.

Contents
========

.. toctree::
   :maxdepth: 2

   Install <install>
   CLI Usage <cli_usage>
   API Usage <api_usage>
   API Documentation <api>
   "create" ReadMe <new_package_readme>
   MSL Developers Guide <developers_guide>
   License <license>
   Authors <authors>
   Release Notes <changelog>

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`

.. _namespace: https://packaging.python.org/guides/packaging-namespace-packages/
.. _Measurement Standards Laboratory of New Zealand: https://measurement.govt.nz/
.. _repositories: https://github.com/MSLNZ
.. _packages: https://pypi.org/search/?q=msl-
