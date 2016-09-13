# -*- coding: utf8 -*-
"""
This module contains the wrapper around librtrs RTR connection manager.
"""

import six
import weakref
import time

from enum import Enum
from six.moves.urllib import parse
from collections import namedtuple, defaultdict
from _rtrlib import ffi, lib

from .util import to_bytestr, is_integer
from .exceptions import *

class RTRManager(object):
    """
    Wrapper arround rtr_manager
    """

    def __init__(self, host, port, refresh_interval=30, expire_interval=600,
                 retry_interval=600, update_fp=ffi.NULL,
                 spki_update_fp=ffi.NULL, status_fp=ffi.NULL,
                 status_fp_data=ffi.NULL
                 ):

        if isinstance(port, six.integer_types):
            port = str(port)
        elif isinstance(port, six.string_types):
            pass
        else:
            raise TypeError('port must be integer or string')

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
                               update_fp,
                               spki_update_fp,
                               status_fp,
                               status_fp_data
                            )

        if ret == lib.RTR_ERROR:
            raise RTRInitError("Error during initilization")
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
        start RTRManager
        """
        lib.rtr_mgr_start(self.rtr_manager_config)

    def stop(self):
        """
        stop RTRManager
        """
        lib.rtr_mgr_stop(self.rtr_manager_config)

    def is_synced(self):
        """
        Detects if RTRManager is in sync
        """
        return lib.rtr_mgr_conf_in_sync(self.rtr_manager_config) == 1

    def wait_for_sync(self):
        """
        Waits until RTRManager is in sync
        """
        while not self.is_synced():
            time.sleep(0.2)

    def validate(self, asn, prefix, mask_len):
        """
        Validates BGP prefix and returns state as PfxvState enum
        """

        if not is_integer(asn):
            raise TypeError("asn must be integer not %s" % type(asn))

        if not is_integer(mask_len):
            raise TypeError("mask_len must be integer not %s" % type(asn))

        lrtr_prefix = ffi.new('struct lrtr_ip_addr *')
        result = ffi.new('enum pfxv_state *')
        lib.lrtr_ip_str_to_addr(to_bytestr(prefix), lrtr_prefix)

        ret = lib.rtr_mgr_validate(self.rtr_manager_config,
                                    asn,
                                    lrtr_prefix,
                                    mask_len,
                                    result
                                   )

        if ret == lib.PFX_ERROR:
            raise PFXException("An error occured during validation")

        return PfxvState(result[0])

class PfxvState(Enum):
    """
    Wrapper for the pfxv_state enum
    """
    valid = lib.BGP_PFXV_STATE_VALID
    not_found = lib.BGP_PFXV_STATE_NOT_FOUND
    invalid = lib.BGP_PFXV_STATE_INVALID

