# -*- coding: utf8 -*-

from __future__ import absolute_import, unicode_literals

import logging
import six

from _rtrlib import ffi, lib
from .exceptions import *


LOG = logging.getLogger(__name__)

def ip_str_to_addr(ip_str):
    addr = ffi.new('struct lrtr_ip_addr *')
    ret = lib.lrtr_ip_str_to_addr(to_bytestr(ip_str), addr)

    if ret != 0:
        raise IpConversionException("String could not be converted")

    return addr

def ip_addr_to_str(ip_addr):
    ip_str = ffi.new('char[]', 128)
    ret = lib.lrtr_ip_addr_to_str(ip_addr, ip_str, 128)

    if ret != 0:
        raise IpConversionException("ip_addr object could not be converted")
    return to_unicodestr(ffi.string(ip_str))

def to_bytestr(string):
    """
    if input string is a unicode string convert to byte string
    """
    if isinstance(string, six.text_type):
        return string.encode('utf8')
    return string

def to_unicodestr(string):
    """
    if input string is a byte string convert to unicode string
    """

    if isinstance(string, six.binary_type):
        return string.decode('utf8')

    return string

def is_integer(var):
    """
    Checks if var is an integer
    """
    return isinstance(var, six.integer_types)

def create_ffi_callback(callback, name):
    """
    Creates a cffi callback.
    """
    LOG.debug('Creating callback %s', name)
    ffi.def_extern(name=name)(callback)
