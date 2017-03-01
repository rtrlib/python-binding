# -*- coding: utf8 -*-
"""
rtrlib.exceptions
-----------------


Module for all custom exceptions
"""

from __future__ import absolute_import, unicode_literals


class RTRlibException(Exception):
    """rtrlib exception base class."""


class RTRInitError(RTRlibException):
    """An error during initialization of the RTR manager occurred."""


class PFXException(RTRlibException):
    """An error during validation occurred."""


class IpConversionException(RTRlibException):
    """An Error during str to address conversion or the reverse occurred."""


class SyncTimeout(RTRlibException):
    """The timeout was reached while waiting for sync."""
