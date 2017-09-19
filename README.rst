MSL Package Manager
===================

|docs|

The **MSL Package Manager** allows you to install, uninstall, update, list and create MSL packages.

All MSL packages are part of the **msl** namespace_. This allows one to split sub-packages and modules
across multiple, separate distribution packages while still maintaining a single, unifying package
structure.

Install
-------

To install the MSL Package Manager run::

   pip install msl-package-manager

Dependencies
++++++++++++
* Python 2.7, 3.3-3.6
* colorama_

Documentation
-------------

The documentation for **MSL Package Manager** can be found `here <http://msl-package-manager.readthedocs.io/en/latest/?badge=latest>`_.

.. |docs| image:: https://readthedocs.org/projects/msl-package-manager/badge/?version=latest
   :target: http://msl-package-manager.readthedocs.io/en/latest/?badge=latest
   :alt: Documentation Status
   :scale: 100%

.. _git: https://git-scm.com
.. _colorama: https://pypi.python.org/pypi/colorama
.. _namespace: https://packaging.python.org/guides/packaging-namespace-packages/