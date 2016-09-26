# -*- coding: utf8 -*-
"""
rtrlib.rtr_manager
------------------

"""

from __future__ import absolute_import, unicode_literals


import time
import logging

from enum import Enum
from ._rtrlib import ffi, lib

import six
import rtrlib.callbacks as callbacks

from .util import to_bytestr, is_integer, ip_str_to_addr
from .exceptions import RTRInitError, PFXException


LOG = logging.getLogger(__name__)


class RTRManager(object):
    """
    Wrapper arround rtr_manager

    :param str host: Hostname or IP of rpki cache server
    :param str|int port: Port number
    :param int refresh_interval: Interval in seconds between serial queries \
        that are sent to the server. Must be >= 1 and <= 86400s (one day).
    :param int expire_interval: Stored validation records will be deleted if \
        cache was unable to refresh data for this period. The value should be \
        twice the refresh_interval. The value must be >= 600s (ten minutes) \
        and <= 172800s (two days).
    :param int retry_interval: This parameter specifies how long to wait \
        (in seconds) before retrying a failed Query. \
        The value must be >= 1s and <= 7200s (two hours).
    """

    def __init__(
            self, host, port, refresh_interval=3600, expire_interval=7200,
            retry_interval=600, status_fp_data=None
        ):

        LOG.debug('Initializing RTR manager')

        if isinstance(port, six.integer_types):
            port = str(port)
        elif isinstance(port, six.string_types):
            pass
        else:
            raise TypeError('port must be integer or string')

        if status_fp_data:
            self.status_fp_data = ffi.new_handle(status_fp_data)
        else:
            self.status_fp_data = ffi.NULL

        self.host = ffi.new('char[]', to_bytestr(host))
        self.port = ffi.new('char[]', to_bytestr(port))

        rtr_manager_config = ffi.new('struct rtr_mgr_config **')

        self.tcp_config = ffi.new('struct tr_tcp_config *')
        self.tr_socket = ffi.new('struct tr_socket *')
        self.rtr_socket = ffi.new('struct rtr_socket []', 1)
        self.rtr_group = ffi.new('struct rtr_mgr_group[]', 1)

        self.tcp_config.host = self.host
        self.tcp_config.port = self.port

        lib.tr_tcp_init(self.tcp_config, self.tr_socket)
        self.rtr_socket[0].tr_socket = self.tr_socket
        self.rtr_group[0].sockets_len = 1
        self.rtr_socketp = ffi.new('struct rtr_socket **', self.rtr_socket)
        self.rtr_group[0].sockets = self.rtr_socketp
        self.rtr_group[0].preference = 1

        ret = lib.rtr_mgr_init(rtr_manager_config,
                               self.rtr_group,
                               1,
                               refresh_interval,
                               expire_interval,
                               retry_interval,
                               callbacks.PFX_UPDATE_CALLBACK,
                               callbacks.SPKI_UPDATE_CALLBACK,
                               callbacks.STATUS_CALLBACK,
                               self.status_fp_data
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

    def start(self):
        """
        Start RTRManager
        """
        LOG.debug("Starting RTR manager")
        lib.rtr_mgr_start(self.rtr_manager_config)

    def stop(self):
        """
        Stop RTRManager
        """
        LOG.debug("Stopping RTR manager")
        lib.rtr_mgr_stop(self.rtr_manager_config)

    def is_synced(self):
        """
        True, if RTRManager is fully synchronized
        """
        return lib.rtr_mgr_conf_in_sync(self.rtr_manager_config) == 1

    def wait_for_sync(self):
        """
        Waits until RTRManager is synchronized
        """
        while not self.is_synced():
            time.sleep(0.2)

    def validate(self, asn, prefix, mask_len):
        """
        Validates BGP prefix and returns state as PfxvState enum
        """

        LOG.debug("Validating %s/%s from AS %s", prefix, mask_len, asn)

        if not is_integer(asn):
            raise TypeError("asn must be integer not %s" % type(asn))

        if not is_integer(mask_len):
            raise TypeError("mask_len must be integer not %s" % type(asn))

        result = ffi.new('enum pfxv_state *')

        ret = lib.rtr_mgr_validate(self.rtr_manager_config,
                                   asn,
                                   ip_str_to_addr(prefix),
                                   mask_len,
                                   result
                                  )

        if ret == lib.PFX_ERROR:
            raise PFXException("An error occurred during validation")

        return PfxvState(result[0])


class PfxvState(Enum):
    """
    Wrapper for the pfxv_state enum
    """
    valid = lib.BGP_PFXV_STATE_VALID
    """A valid certificate for the pfx_record exists"""

    not_found = lib.BGP_PFXV_STATE_NOT_FOUND
    """No certificate for the route exists"""

    invalid = lib.BGP_PFXV_STATE_INVALID
    """One or more records that match the input prefix exists in the pfx_table, but the prefix max_len or ASN doesn't match."""
