|docs|

=============
rtrlib-python
=============

rtrlib-python is a cffi based python binding for rtrlib_.

.. _rtrlib: https://github.com/rtrlib/rtrlib

Sphinx docs can be found in the docs directory and build with ``make html``.

for usage examples see the tools directory

Features
--------
Features supported so far:

- Prefix validation
- rtr_mgr callbacks



Install Instructions
--------------------

Requirements
''''''''''''
- python 2.7 or python 3
- cffi>=1.4.0
- enum34
- six

and a c compiler at build time.

If you are using virtualenv the Requirements are installed automatically during the install step, otherwise you have to use your platforms package management tool or just run pip install -r requirements.txt.


Download and Installation
'''''''''''''''''''''''''

- ``git clone https://github.com/rtrlib/python-binding.git``
- ``cd python-binding``
- ``python setup.py build``
- ``python setup.py install``


.. |docs| image:: https://readthedocs.org/projects/python-rtrlib/badge/?version=latest
    :target: http://python-rtrlib.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status
