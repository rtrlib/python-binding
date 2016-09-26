#!/usr/bin/env python
# -*- coding: utf8 -*-

from setuptools import setup


setup(
    name='rtrlib',
    version='0.1',
    description='rtrlib binding',
    author='Marcel Röthke',
    author_email='marcel.roethke@haw-hamburg.de',
    url='https://github.com/mroethke/rtrlib-python',
    packages=['rtrlib'],
    include_package_data=True,
    license='Apache 2.0',
    zip_safe=False,
    classifiers=(
        'Development Status :: 3 - Alpha'
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License'
        'Natural Language :: English',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy'
    ),
    setup_requires=["cffi>=1.4.0"],
    cffi_modules=["ffi_build.py:ffibuilder"],
    install_requires=["cffi>=1.4.0", "six", 'enum34'],
)
