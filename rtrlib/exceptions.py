# -*- coding: utf8 -*-
"""
rtrlib.exceptions
-----------------


Module for all custom exceptions
"""

from __future__ import absolute_import, unicode_literals


class RTRlibException(Exception):
    """rtrlib exception base class"""

class RTRInitError(RTRlibException):
    """An error during initialization of occurred"""


class PFXException(RTRlibException):
    """An error occurred during validation"""

class IpConversionException(RTRlibException):
    """An Error during str to address conversion or the reverse occurred"""
