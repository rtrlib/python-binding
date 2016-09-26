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
rtrlib-python is not on pypi yet, but you can just run ``python setup.py install``.
It is probably a good idea to use a virtualenv.

Requirements
''''''''''''
- python 2.7 or python 3
- cffi>=1.4.0
- enum34
- six

and a c compiler for building the module.
