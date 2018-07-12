HPV Information Centre data manager
#######################################

|docs|

The HPV Information Centre data manager provide methods and utilities to upload scientific data from different sources and perform different (pluggable) data validation procedures to update the HPV Information Centre scientific databases

This project is being developed by the ICO/IARC Information Centre on HPV and Cancer and will be used in our data management tasks.

.. image:: HPV_infocentre.png
   :height: 50px
   :align: center
   :target: http://www.hpvcentre.net

.. |docs| image:: https://readthedocs.org/projects/infocentre-data-manager/badge/?version=stable
    :alt: Documentation Status
    :scale: 100%
    :target: https://infocentre-data-manager.readthedocs.io/en/stable/?badge=stable

Features
============

TODO

Installation
============

Package
-------

.. code:: bash

 git clone https://github.com/hpv-information-centre/reportcompiler-ic-data-manager
 cd reportcompiler-ic-data-manager/scripts
 ./install_package.sh


Documentation
-------------

To generate HTML documentation:

.. code:: bash

 scripts/compile_docs.sh

This project uses Sphinx for documentation, so for other formats please use 'make' with the appropriate parameters on the doc directory.


Git hooks setup
---------------

.. code:: bash

 scripts/prepare_hooks.sh