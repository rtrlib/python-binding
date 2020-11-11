# -*- coding: utf8 -*-
"""
rtrlib.rtr_manager
------------------

"""

from __future__ import absolute_import, unicode_literals


import time
import logging
import signal
import threading

from enum import Enum
from _rtrlib import ffi, lib

import rtrlib.callbacks as callbacks
import rtrlib.records as records

from .util import (to_bytestr,
                   is_integer,
                   is_string,
                   ip_str_to_addr,
                   CallbackGenerator
                   )
from .exceptions import RTRInitError, PFXException, SyncTimeout


LOG = logging.getLogger(__name__)


class RTRManager(object):
    r"""
    Wrapper around rtr_manager.

    :param str host: Hostname or IP of rpki cache server
    :type host: str

    :param port: Port number
    :type port: int

    :param int refresh_interval: Interval in seconds between serial queries \
        that are sent to the server. Must be >= 1 and <= 86400s (one day).
    :type refresh_interval: int

    :param int expire_interval: Stored validation records will be deleted if \
        cache was unable to refresh data for this period. The value should be \
        twice the refresh_interval. The value must be >= 600s (ten minutes) \
        and <= 172800s (two days).
    :type expire_interval: int

    :param int retry_interval: This parameter specifies how long to wait \
        (in seconds) before retrying a failed Query. \
        The value must be >= 1s and <= 7200s (two hours).
    :type retry_interval: int

    :param function status_callback: status callback, \
        called on status changes of the rtr manager
    :type status_callback: function

    :param status_callback_data: arbitrary data object passed to the \
        callback.
    :type status_callback_data: object

    :param pfx_update_callback: pfx update callback \
            called every time a pfx update is received
    :type pfx_update_callback: function

    :param pfx_update_callback_data: data passed to the pfx update callback

    :param spki_update_callback: spki update callback \
            called every time a spki update is received
    :type spki_update_callback: function

    :param spki_update_callback_data: data passed to the spki update callback

    :raises RTRInitError:

    """

    def __init__(
                self,
                host,
                port,
                refresh_interval=3600,
                expire_interval=7200,
                retry_interval=600,
                status_callback=None,
                status_callback_data=None,
                pfx_update_callback=None,
                pfx_update_callback_data=None,
                spki_update_callback=None,
                spki_update_callback_data=None,
            ):

        LOG.debug('Initializing RTR manager')

        if is_integer(port):
            port = str(port)
        elif is_string(port):
            pass
        else:
            raise TypeError('port must be integer or string')

        self._status_callback_data = status_callback_data
        self._handle = ffi.new_handle(self)

        if status_callback:
            self._status_callback = status_callback
            cffi_callback = lib.rtr_mgr_status_callback
        else:
            self._status_callback = ffi.NULL
            cffi_callback = ffi.NULL

        self._pfx_update_callback_data = pfx_update_callback_data
        if pfx_update_callback:
            self._pfx_update_callback = pfx_update_callback
            pfx_cffi_callback = lib.pfx_update_callback
        else:
            self._pfx_update_callback = ffi.NULL
            pfx_cffi_callback = ffi.NULL

        self._spki_update_callback_data = spki_update_callback_data
        if spki_update_callback:
            self._spki_update_callback = spki_update_callback
            spki_cffi_callback = lib.spki_update_callback
        else:
            self._spki_update_callback = ffi.NULL
            spki_cffi_callback = ffi.NULL

        self.host = ffi.new('char[]', to_bytestr(host))
        self.port = ffi.new('char[]', to_bytestr(port))

        rtr_manager_config = ffi.new('struct rtr_mgr_config **')

        self.tcp_config = ffi.new('struct tr_tcp_config *')
        self.tr_socket = ffi.new('struct tr_socket *')
        self.rtr_socket = ffi.new('struct rtr_socket_wrapper *')
        self.rtr_group = ffi.new('struct rtr_mgr_group[]', 1)

        self.tcp_config.host = self.host
        self.tcp_config.port = self.port

        lib.tr_tcp_init(self.tcp_config, self.tr_socket)
        self.rtr_socket.rtr_socket.tr_socket = self.tr_socket
        self.rtr_socket[0].data = self._handle
        self.rtr_group[0].sockets_len = 1
        self.rtr_socketp = ffi.new('struct rtr_socket **', ffi.cast("struct rtr_socket *", self.rtr_socket))
        self.rtr_group[0].sockets = self.rtr_socketp
        self.rtr_group[0].preference = 1

        ret = lib.rtr_mgr_init(rtr_manager_config,
                               self.rtr_group,
                               1,
                               refresh_interval,
                               expire_interval,
                               retry_interval,
                               pfx_cffi_callback,
                               spki_cffi_callback,
                               cffi_callback,
                               self._handle
                               )

        if ret == lib.RTR_ERROR:
            raise RTRInitError("Error during initialization")
        elif ret == lib.RTR_INVALID_PARAM:
            raise RTRInitError("refresh_interval or the expire_interval "
                               "is invalid.")

        self.rtr_manager_config = rtr_manager_config[0]

    def __del__(self):
        if hasattr(self, "rtr_manager_config"):
            lib.rtr_mgr_free(self.rtr_manager_config)

    def __enter__(self):
        self.start()
        self.wait_for_sync()

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()

        return False

    def start(self, wait=True, timeout=5):
        """
        Start RTRManager.

        :param bool wait: Wait for the manager to finish sync
        :param int timeout:

        :raises SyncTimeout: Raised if timeout is reached,
            this does not mean that the sync failed,
            only that it did not finish in time.
        """
        LOG.debug("Starting RTR manager")
        lib.rtr_mgr_start(self.rtr_manager_config)

        if wait:
            self.wait_for_sync(timeout)

    def stop(self):
        """Stop RTRManager."""
        LOG.debug("Stopping RTR manager")
        lib.rtr_mgr_stop(self.rtr_manager_config)

    def is_synced(self):
        """
        Check if RTRManager is fully synchronized.

        :rtype: bool
        """
        return lib.rtr_mgr_conf_in_sync(self.rtr_manager_config) == 1

    def wait_for_sync(self, timeout=5):
        """
        Wait until RTRManager is synchronized.

        :param int timeout:

        :raises SyncTimeout: Raise if timeout is reached,
            this does not mean that the sync failed,
            only that it did not finish in time.
        """
        def handler(signum, frame):
            raise SyncTimeout()

        if timeout > 0:
            signal.signal(signal.SIGALRM, handler)
            signal.alarm(timeout)

        while not self.is_synced():
            time.sleep(0.2)

        signal.alarm(0)

    def validate(self, asn, prefix, mask_len):
        """
        Validate BGP prefix and returns state as PfxvState enum.

        :param asn: autonomous system number
        :type asn: int

        :param prefix: ip address
        :type prefix: str

        :param mask_len: length of the subnet mask
        :type mask_len: int

        :rtype: ValidationResult
        """
        LOG.debug("Validating %s/%s from AS %s", prefix, mask_len, asn)

        if not is_integer(asn):
            raise TypeError("asn must be integer not %s" % type(asn))

        if not is_integer(mask_len):
            raise TypeError("mask_len must be integer not %s" % type(asn))

        result = ffi.new('enum pfxv_state *')

        reason = ffi.new('struct pfx_record **')
        reason[0] = ffi.NULL
        reason_length = ffi.new('unsigned int *')
        reason_length[0] = 0

        ret = lib.pfx_table_validate_r(self.rtr_socket[0].pfx_table,
                                       reason,
                                       reason_length,
                                       asn,
                                       ip_str_to_addr(prefix),
                                       mask_len,
                                       result
                                       )

        if ret == lib.PFX_ERROR:
            raise PFXException("An error occurred during validation")

        return ValidationResult(prefix,
                                mask_len,
                                asn,
                                result[0],
                                reason,
                                reason_length[0])

    def for_each_ipv4_record(self, callback, data):
        r"""
        Iterate over all ipv4 records of the pfx table.

        callback must take two arguments, the pfx_record and the data object.

        For a more pythonic alternative see :py:meth:`ipv4_records`

        :param callable callback: called for every record in the pfx table
        :param object data: arbitrary data object \
            that is passed to the callback function
        """
        data_handle = ffi.new_handle((callback, data))

        lib.rtr_mgr_for_each_ipv4_record(
            self.rtr_manager_config,
            lib.pfx_table_callback,
            data_handle
            )

    def ipv4_records(self):
        r"""
        Return iterator over all ipv4 records in the pfx table.

        This iterator utilises threads to execute retrieve the records. \
        If that is a problem for you take a look at \
        :py:meth:`for_each_ipv4_record`.

        :rtype: Iterator
        """
        def callback(record, data):
            LOG.debug('Putting "%s" in queue', record)
            data.put_nowait(records.copy_pfx_record(record))

        generator = CallbackGenerator(self.for_each_ipv4_record, callback)
        return generator

    def for_each_ipv6_record(self, callback, data):
        r"""
        Iterate over all ipv6 records of the pfx table.

        callback must take two arguments, the pfx_record and the data object.

        For a more pythonic alternative see :py:meth:`ipv6_records`

        :param callable callback: called for every record in the pfx table
        :param object data: arbitrary data object \
            that is passed to the callback function
        """
        data_handle = ffi.new_handle((callback, data))

        lib.rtr_mgr_for_each_ipv6_record(
            self.rtr_manager_config,
            lib.pfx_table_callback,
            data_handle
            )

    def ipv6_records(self):
        r"""
        Return iterator over all ipv6 records in the pfx table.

        This iterator utilises threads to execute retrieve the records. \
        If that is a problem for you take a look at \
        :py:meth:`for_each_ipv6_record`.

        :rtype: Iterator
        """
        def callback(record, data):
            LOG.debug('Putting "%s" in queue', record)
            data.put_nowait(records.copy_pfx_record(record))

        generator = CallbackGenerator(self.for_each_ipv6_record, callback)
        return generator


class PfxvState(Enum):
    """Wrapper for the pfxv_state enum."""

    valid = lib.BGP_PFXV_STATE_VALID
    """A valid certificate for the pfx_record exists"""

    not_found = lib.BGP_PFXV_STATE_NOT_FOUND
    """No certificate for the route exists"""

    invalid = lib.BGP_PFXV_STATE_INVALID
    r"""
    One or more records that match the input prefix exists in the pfx_table, \
    but the prefix max_len or ASN doesn't match.
    """


class Reason(object):
    """A Reason upon which a validation decision was made.

    :param prefix_length: Length of the validated prefix
    :type prefix_length: int

    :param asn: As number of the validated prefix
    :type asn: As number of the validated prefix

    :param record: PFXRecord
    :type record: PFXRecord
    """

    def __init__(self, prefix_length, asn, record):
        if (not ffi.typeof(record) is ffi.typeof("struct pfx_record *") and
                not ffi.typeof(record) is ffi.typeof("struct pfx_record")):
            raise TypeError("record must be struct pfx_record *")

        self.prefix_length = prefix_length
        self.asn = asn
        self.record = records.PFXRecord(record)

    def __str__(self,):
        return '{}: as_valid = {}, length_valid = {}'.format(self.record, self.as_valid, self.length_valid)

    @property
    def as_valid(self):
        """True if as is valid."""
        return self.record.asn == self.asn

    @property
    def as_invalid(self):
        """True is as is invalid."""
        return not self.as_valid

    @property
    def length_valid(self):
        """True if prefix length is valid."""
        return self.record.min_len <= self.prefix_length <= self.record.max_len

    @property
    def length_invalid(self):
        """True if prefix length is invalid."""
        return not self.length_valid


class ValidationResult(object):
    """
    Wrapper class for validation result.

    :param prefix: The prefix that was validated
    :type prefix: str

    :param prefix_length: The length of the prefix
    :type prefix_length: int

    :param asn: The ASN the prefix is supposed to be in.
    :param asn: int

    :param state: Validation state
    :type state: enum pfxv_state *

    :param reason_records: Array of PFXRecords the decision is based on
    :type reason_records: struct pfx_record **

    :param reason_len: Length of reason_records
    :type reason_len: int
    """

    def __init__(self,
                 prefix,
                 prefix_length,
                 asn,
                 state,
                 reason_records=None,
                 reason_len=0
                 ):
        self._state = PfxvState(state)
        self._prefix = prefix
        self._prefix_length = prefix_length
        self._asn = asn

        if (reason_records and reason_len and
                ffi.typeof(reason_records) is ffi.typeof('struct pfx_record **')):

            self._reason = []
            self._reason_records = reason_records
            for record in ffi.unpack(reason_records[0], reason_len):
                self._reason.append(Reason(prefix_length, asn, record))

        elif (not ffi.typeof(reason_records) is ffi.typeof('struct pfx_record **')):
            raise TypeError("reason_records must be struct pfx_record **")
        else:
            self._reason = None
            self._reason_records = None

    def __del__(self,):
        if self._reason_records:
            lib.free(self._reason_records[0])

    def __str__(self,):
        return '{}/{} AS{}: {}'.format(self._prefix,
                                       self._prefix_length,
                                       self._asn,
                                       self.state)

    @property
    def state(self):
        """Validation state."""
        return self._state

    @property
    def is_invalid(self):
        """Return true if prefix is invalid."""
        return self.state == PfxvState.invalid

    @property
    def is_valid(self):
        """True if prefix is valid."""
        return self.state == PfxvState.valid

    @property
    def not_found(self):
        """True if prefix could not be found."""
        return self.state == PfxvState.not_found

    @property
    def as_invalid(self):
        r"""True if at least one matching record has a different as number \
        and state is invalid.
        """
        return (self.is_invalid and
                any(reason.as_invalid for reason in self._reason))

    @property
    def length_invalid(self):
        r"""True if at least one matching record has a miss matching prefix \
         length and state is invalid.
         """
        return (self.is_invalid and
                any(reason.length_invalid for reason in self._reason))

    @property
    def reason(self):
        """List of :class:`.Reason` ."""
        return self._reason
