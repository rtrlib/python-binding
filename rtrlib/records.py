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
    """Wrapper around the pfx_record struct."""

    def __init__(self, record):
        if (not ffi.typeof(record) is ffi.typeof("struct pfx_record *") and
                not ffi.typeof(record) is ffi.typeof("struct pfx_record")):
            raise TypeError("Type of record must be struct pfx_record *")

        self._record = record

    @property
    def asn(self):
        """Origin AS number."""
        return self._record.asn

    @property
    def max_len(self):
        """Maximum prefix length."""
        return self._record.max_len

    @property
    def min_len(self):
        """Minimum prefix length."""
        return self._record.min_len

    @property
    def prefix(self):
        """IP prefix."""
        return ip_addr_to_str(ffi.addressof(self._record.prefix))

    @property
    def socket(self):
        """:class:`.RTRSocket` this record was received in."""
        return RTRSocket(self._record.socket)

    def __str__(self):
        return "{prefix}/{min}-{max} {asn}".format(prefix=self.prefix,
                                                   min=self.min_len,
                                                   max=self.max_len,
                                                   asn=self.asn
                                                   )


def copy_pfx_record(record):
    """
    Copy a pfx record.

    :param PFXRecord record: The record that should be copied
    :rtype: PFXRecord
    """
    if not isinstance(record, PFXRecord):
        raise TypeError("Type of record must be struct pfx_record *")

    cdata = record._record
    new_record = ffi.new('struct pfx_record *')
    new_record.asn = cdata.asn
    new_record.prefix = cdata.prefix
    new_record.min_len = cdata.min_len
    new_record.max_len = cdata.max_len
    new_record.socket = cdata.socket

    return PFXRecord(new_record)


class SPKIRecord(object):
    """Wrapper around the spki_record struct."""

    def __init__(self, record):
        if not ffi.typeof(record) is ffi.typeof("struct spki_record *"):
            raise TypeError("Type of record must be struct spki_record *")

        self._record = record

    @property
    def asn(self):
        """Origin AS number."""
        return self._record.asn

    @property
    def ski(self):
        """Subject Key Identifier."""
        return self._record.ski

    @property
    def socket(self):
        """:class:`.RTRSocket` this record was received in."""
        return RTRSocket(self._record.socket)

    @property
    def spki(self):
        """Subject public key info."""
        return self._record.spki
