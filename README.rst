MSL-Package-Manager
===================

|docs| |pypi|

The **MSL Package Manager** allows you to install, uninstall, update, list and create packages
that are used at the `Measurement Standards Laboratory of New Zealand`_.

All MSL packages are part of the **msl** namespace_. This allows one to split sub-packages and modules
across multiple, separate distribution packages while still maintaining a single, unifying package
structure.

Install
-------

To install the **MSL Package Manager** run:

.. code-block:: console

   pip install msl-package-manager

Dependencies
++++++++++++
* Python 2.7, 3.4+
* pip_
* setuptools_
* colorama_

Documentation
-------------

The documentation for **MSL Package Manager** can be found here_.

.. |docs| image:: https://readthedocs.org/projects/msl-package-manager/badge/?version=latest
   :target: https://msl-package-manager.readthedocs.io/en/latest/
   :alt: Documentation Status
   :scale: 100%

.. |pypi| image:: https://badge.fury.io/py/msl-package-manager.svg
   :target: https://badge.fury.io/py/msl-package-manager

.. _pip: https://pypi.org/project/pip/
.. _setuptools: https://pypi.org/project/setuptools/
.. _colorama: https://pypi.org/project/colorama/
.. _namespace: https://packaging.python.org/guides/packaging-namespace-packages/
.. _here: https://msl-package-manager.readthedocs.io/en/latest/
.. _Measurement Standards Laboratory of New Zealand: https://measurement.govt.nz/
