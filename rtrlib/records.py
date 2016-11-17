# -*- coding: utf8 -*-
"""
rtrlib.records
--------------

Collection of wrappers for \*record structs of rtrlib
"""

from __future__ import absolute_import, unicode_literals

from _rtrlib import ffi

from .util import ip_addr_to_str
from .rtr_socket import RTRSocket

class PFXRecord(object):
    """
    Wrapper around the pfx_record struct
    """

    def __init__(self, record):
        self._record = record

    @property
    def asn(self):
        """
        Origin AS number
        """
        return self._record.asn

    @property
    def max_len(self):
        """
        Maximum prefix length
        """
        return self._record.max_len

    @property
    def min_len(self):
        """
        Minimum prefix length
        """
        return self._record.min_len

    @property
    def prefix(self):
        """
        IP prefix
        """
        return ip_addr_to_str(ffi.addressof(self._record.prefix))

    @property
    def socket(self):
        """
        :class:`~rtrlib.rtr_socket.RTRSocket` this record was received in
        """
        return RTRSocket(self._record.socket)


class SPKIRecord(object):
    """
    Wrapper around the spki_record struct
    """

    def __init__(self, record):
        self._record = record

    @property
    def asn(self):
        """
        Origin AS number
        """
        return self._record.asn


    @property
    def ski(self):
        """
        Subject Key Identifier
        """
        return self._record.ski

    @property
    def socket(self):
        """
        :class:`~rtrlib.rtr_socket.RTRSocket` this record was received in
        """
        return RTRSocket(self._record.socket)

    @property
    def spki(self):
        """
        Subject public key info
        """
        return self._record.spki
