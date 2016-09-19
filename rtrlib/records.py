# -*- coding: utf8 -*-

from _rtrlib import ffi

from .util import ip_addr_to_str
from .rtr_socket import RTRSocket

class PFXRecord:

    def __init__(self, record):
        self._record = record

    @property
    def asn(self):
        return self._record.asn

    @property
    def max_len(self):
        return self._record.max_len

    @property
    def min_len(self):
        return self._record.min_len

    @property
    def prefix(self):
        return ip_addr_to_str(ffi.addressof(self._record.prefix))

    @property
    def socket(self):
        return RTRSocket(self._record.socket)


class SPKIRecord:

    def __init__(self, record):
        self._record = record

    @property
    def asn(self):
        return self._record.asn


    @property
    def ski(self):
        return self._record.ski

    @property
    def socket(self):
        return RTRSocket(self._record.socket)

    @property
    def spki(self):
        return self._record.spki



