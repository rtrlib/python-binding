#!/usr/bin/env python
# -*- coding: utf8 -*-

from setuptools import setup

from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))


with open(path.join(here, 'README.rst'), encoding='utf8') as f:
    long_description = f.read()

setup(
    name='rtrlib',
    version='0.1',
    description='rtrlib binding',
    long_description=long_description,
    author='Marcel Röthke',
    author_email='marcel.roethke@haw-hamburg.de',
    url='https://github.com/mroethke/rtrlib-python',
    packages=['rtrlib'],
    include_package_data=True,
    license='MIT',
    zip_safe=False,
    classifiers=(
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy'
    ),
    setup_requires=["cffi>=1.6.0"],
    cffi_modules=["ffi_build.py:ffibuilder"],
    install_requires=["cffi>=1.6.0", "six", 'enum34'],
)
