# -*- coding: utf8 -*-
"""
This module contains the wrapper around librtrs RTR connection manager.
"""

import six
import weakref
import time
import logging

from enum import Enum
from six.moves.urllib import parse
from collections import namedtuple, defaultdict
from _rtrlib import ffi, lib

from .util import *
from .exceptions import *
from .manager_status import ManagerStatus
from .rtr_socket import RTRSocket
from .manager_group import ManagerGroup
from .records import PFXRecord, SPKIRecord

LOG = logging.getLogger(__name__)

class RTRManager(object):
    """
    Wrapper arround rtr_manager
    """

    def __init__(self, host, port, refresh_interval=30, expire_interval=600,
                 retry_interval=600, pfx_update_fp=ffi.NULL,
                 spki_update_fp=ffi.NULL, status_fp=ffi.NULL,
                 status_fp_data=None
                 ):

        LOG.debug('Initilizing RTR manager')

        if isinstance(port, six.integer_types):
            port = str(port)
        elif isinstance(port, six.string_types):
            pass
        else:
            raise TypeError('port must be integer or string')

        if pfx_update_fp != ffi.NULL:
            create_ffi_callback(pfx_update_callback_wrapper(pfx_update_fp), "pfx_update_callback")
            pfx_update_fp = lib.pfx_update_callback

        if spki_update_fp != ffi.NULL:
            create_ffi_callback(spki_update_callback_wrapper(spki_update_fp), "spki_update_callback")
            spki_update_fp = lib.spki_update_callback

        if status_fp != ffi.NULL:
            create_ffi_callback(status_callback_wrapper(status_fp), "rtr_mgr_status_callback")
            status_fp = lib.rtr_mgr_status_callback

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
                               pfx_update_fp,
                               spki_update_fp,
                               status_fp,
                               self.status_fp_data
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
        LOG.debug("Starting RTR manager")
        lib.rtr_mgr_start(self.rtr_manager_config)

    def stop(self):
        """
        stop RTRManager
        """
        LOG.debug("Stoping RTR manager")
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
            raise PFXException("An error occured during validation")

        return PfxvState(result[0])

class PfxvState(Enum):
    """
    Wrapper for the pfxv_state enum
    """
    valid = lib.BGP_PFXV_STATE_VALID
    not_found = lib.BGP_PFXV_STATE_NOT_FOUND
    invalid = lib.BGP_PFXV_STATE_INVALID



def status_callback_wrapper(func):
    def inner(rtr_mgr_group, group_status, rtr_socket, data):
        LOG.debug("Calling status callback")
        func(
             ManagerGroup(rtr_mgr_group),
             ManagerStatus(group_status),
             RTRSocket(rtr_socket),
             ffi.from_handle(data)
            )

    return inner

def pfx_update_callback_wrapper(func):
    def inner(pfx_table, pfx_record, added):
        LOG.debug("Calling pfx update callback")
        func(
             PFXRecord(pfx_record),
             added,
            )
    return inner

def spki_update_callback_wrapper(func):
    def inner(record, added):
        LOG.debug("Calling spki update callback")
        func(
             SPKIRecord(record),
             added,
             )
    return inner
