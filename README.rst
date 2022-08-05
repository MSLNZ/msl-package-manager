MSL-Package-Manager
===================

|docs| |github tests| |pypi|

The **MSL Package Manager** allows one to install, uninstall, update, list and create packages
that are used at the `Measurement Standards Laboratory of New Zealand`_.

All MSL packages that start with ``msl-`` are part of the **msl** namespace_. This allows one to
split sub-packages and modules across multiple, separate distribution packages while still
maintaining a single, unifying package structure.

Install
-------

To install the **MSL Package Manager** run:

.. code-block:: console

   pip install msl-package-manager

Dependencies
++++++++++++
* Python 2.7, 3.5+
* setuptools_
* colorama_

Documentation
-------------

The documentation for **MSL Package Manager** can be found here_.

.. |docs| image:: https://readthedocs.org/projects/msl-package-manager/badge/?version=latest
   :target: https://msl-package-manager.readthedocs.io/en/stable/
   :alt: Documentation Status
   :scale: 100%

.. |github tests| image:: https://github.com/MSLNZ/msl-package-manager/actions/workflows/run-tests.yml/badge.svg
   :target: https://github.com/MSLNZ/msl-package-manager/actions/workflows/run-tests.yml

.. |pypi| image:: https://badge.fury.io/py/msl-package-manager.svg
   :target: https://badge.fury.io/py/msl-package-manager

.. _setuptools: https://pypi.org/project/setuptools/
.. _colorama: https://pypi.org/project/colorama/
.. _namespace: https://packaging.python.org/guides/packaging-namespace-packages/
.. _here: https://msl-package-manager.readthedocs.io/en/stable/
.. _Measurement Standards Laboratory of New Zealand: https://measurement.govt.nz/
