# -*- coding: utf8 -*-
"""
Module for all custom exceptions.
"""

from __future__ import absolute_import, unicode_literals


class RtrlibException(Exception):
    """rtrlib exception base class"""

class RTRInitError(RtrlibException):
    """An error during initilization of occured"""


class PFXException(RtrlibException):
    """An error occured during validation"""

class IpConversionException(RtrlibException):
    """An Error during str to address conversion or the reverse occured"""
