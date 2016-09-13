# -*- coding: utf8 -*-
"""
Module for all custom exceptions.
"""


class RtrlibException(Exception):
    """rtrlib exception base class"""

class RTRInitError(RtrlibException):
    """An error during initilization of occured"""


class PFXException(Exception):
    """An error occured during validation"""
