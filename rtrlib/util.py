# -*- coding: utf8 -*-

import six

def to_bytestr(string):
    """
    if input string is a unicode string convert to byte string
    """
    if isinstance(string, six.text_type):
        return string.encode('utf8')
    return string
