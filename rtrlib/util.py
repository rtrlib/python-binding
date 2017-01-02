# -*- coding: utf8 -*-
"""
rtrlib.util
-----------


Utility functions and wrapper
"""

from __future__ import absolute_import, unicode_literals

import logging
import six

from _rtrlib import ffi, lib
from .exceptions import IpConversionException


LOG = logging.getLogger(__name__)

def ip_str_to_addr(ip_str):
    """
    Converts an IP from string to rtrlib internal representation

    :param str ip_str: IP address IPv4 and IPv6 are supported
    :return The IP address as cdata struct lrtr_ip_addr
    """
    addr = ffi.new('struct lrtr_ip_addr *')
    ret = lib.lrtr_ip_str_to_addr(to_bytestr(ip_str), addr)

    if ret != 0:
        raise IpConversionException("String could not be converted")

    return addr

def ip_addr_to_str(ip_addr):
    """
    Converts an IP from rtrlib internal to string representation

    :param cdata ip_addr: IP address as cdata struct lrtr_ip_addr
    :return IP address as string
    """
    ip_str = ffi.new('char[]', 128)
    ret = lib.lrtr_ip_addr_to_str(ip_addr, ip_str, 128)

    if ret != 0:
        raise IpConversionException("ip_addr object could not be converted")
    return to_unicodestr(ffi.string(ip_str))

def to_bytestr(string):
    """
    if input string is a Unicode string convert to byte string
    """
    if isinstance(string, six.text_type):
        return string.encode('utf8')
    return string

def to_unicodestr(string):
    """
    if input string is a byte string convert to Unicode string
    """

    if isinstance(string, six.binary_type):
        return string.decode('utf8')

    return string

def is_integer(var):
    """
    Checks if var is an integer
    """
    return isinstance(var, six.integer_types)

def is_string(var):
    """
    Checks if var is a string
    """
    return isinstance(var, six.string_types)
