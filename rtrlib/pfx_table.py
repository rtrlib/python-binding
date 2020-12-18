# -*- coding: utf8 -*-
"""
rtrlib.rtr_manager
------------------

"""

from __future__ import absolute_import, unicode_literals


from .exceptions import PFXException
from .rtr_manager import ValidationResult
from .util import ip_str_to_addr

from _rtrlib import ffi, lib


class PfxTable(object):
    """
    Wrapper class around pfx_table.

    """

    def __init__(self):
        # allocate pfx_table
        self.pfx_table = ffi.new('struct pfx_table *')
        # initialize it
        lib.pfx_table_init(self.pfx_table,
                           ffi.NULL)
        self.closed = False

    def add_record(self, asn, ip, min_length, max_length):
        """
        Add a BGP prefix to the table.

        :param asn: autonomous system number
        :type asn: int

        :param ip: ip address
        :type ip: str

        :param min_length: minimum length of the subnet mask
        :type min_length: int

        :param max_length: minimum length of the subnet mask
        :type max_length: int
        """

        record = ffi.new('struct pfx_record *')
        prefix = ffi.new('struct lrtr_ip_addr *')
        lib.lrtr_ip_str_to_addr(ip.encode('ascii'), prefix)

        record.asn = asn
        record.min_len = min_length
        record.max_len = max_length
        record.socket = ffi.NULL
        record.prefix = prefix[0]

        lib.pfx_table_add(self.pfx_table, record)

    def remove_record(self, asn, ip, min_length, max_length):
        """
        Add a BGP prefix to the table.

        :param asn: autonomous system number
        :type asn: int

        :param ip: ip address
        :type ip: str

        :param min_length: minimum length of the subnet mask
        :type min_length: int

        :param max_length: minimum length of the subnet mask
        :type max_length: int
        """

        record = ffi.new('struct pfx_record *')
        prefix = ffi.new('struct lrtr_ip_addr *')
        lib.lrtr_ip_str_to_addr(ip.encode('ascii'), prefix)

        record.asn = asn
        record.min_len = min_length
        record.max_len = max_length
        record.socket = ffi.NULL
        record.prefix = prefix[0]

        lib.pfx_table_remove(self.pfx_table, record)

    def validate(self, asn, prefix, mask_len):
        """
        Validate BGP prefix and returns state as ValidationResult object.
        The reason list in the returned result will be empty.

        :param asn: autonomous system number
        :type asn: int

        :param prefix: ip address
        :type prefix: str

        :param mask_len: length of the subnet mask
        :type mask_len: int

        :rtype: ValidationResult
        """

        result = ffi.new('enum pfxv_state *')

        ret = lib.pfx_table_validate(self.pfx_table,
                                     asn,
                                     ip_str_to_addr(prefix),
                                     mask_len,
                                     result)

        if ret == lib.PFX_ERROR:
            raise PFXException("An error occurred during validation")

        return ValidationResult(prefix,
                                mask_len,
                                asn,
                                result[0])

    def validate_r(self, asn, prefix, mask_len):
        """
        Validate BGP prefix and returns state as ValidationResult object.
        The reason list in the returned result will contain a list of Reason objects.

        :param asn: autonomous system number
        :type asn: int

        :param prefix: ip address
        :type prefix: str

        :param mask_len: length of the subnet mask
        :type mask_len: int

        :rtype: ValidationResult
        """

        result = ffi.new('enum pfxv_state *')

        reason = ffi.new('struct pfx_record **')
        reason[0] = ffi.NULL
        reason_length = ffi.new('unsigned int *')
        reason_length[0] = 0

        ret = lib.pfx_table_validate_r(self.pfx_table,
                                       reason,
                                       reason_length,
                                       asn,
                                       ip_str_to_addr(prefix),
                                       mask_len,
                                       result)

        if ret == lib.PFX_ERROR:
            raise PFXException("An error occurred during validation")

        return ValidationResult(prefix,
                                mask_len,
                                asn,
                                result[0],
                                reason,
                                reason_length[0])

    def close(self):
        if not self.closed:
            lib.pfx_table_free(self.pfx_table)
            self.closed = True

    def __enter__(self):
        return self

    def __del__(self):
        self.close()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False
