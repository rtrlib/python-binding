# -*- coding: utf8 -*-

import six

def to_bytestr(string):
    """
    if input string is a unicode string convert to byte string
    """
    if isinstance(string, six.text_type):
        return string.encode('utf8')
    return string

def is_integer(var):
    """
    Checks if var is an integer
    """
    return isinstance(var, six.integer_types)
