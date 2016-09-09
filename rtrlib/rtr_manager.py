# -*- coding: utf8 -*-

import six
import weakref
import time

from enum import Enum
from six.moves.urllib import parse
from collections import namedtuple, defaultdict
from _rtrlib import ffi, lib

from .util import to_bytestr

class RTRManager(object):

    #socket_group = namedtuple('preference', 'sockets')
    #tcp_socket = namedtuple('hostname', 'port', 'BindAddress')

    def __init__(self, host, port, refresh_interval=30, expire_interval=600,
                 retry_interval=600, update_fp=ffi.NULL,
                 spki_update_fp=ffi.NULL, status_fp=ffi.NULL,
                 status_fp_data=ffi.NULL
                 ):

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

        print(lib.rtr_mgr_init(rtr_manager_config,
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
        )

        self.rtr_manager_config = rtr_manager_config[0]

    def __del__(self):
        lib.rtr_mgr_free(self.rtr_manager_config)

    def start(self):
        """
        start RTRManager
        """
        print(lib.rtr_mgr_start(self.rtr_manager_config))

    def stop(self):
        """
        stop RTRManager
        """
        print(lib.rtr_mgr_stop(self.rtr_manager_config))

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
        lrtr_prefix = ffi.new('struct lrtr_ip_addr *')
        result = ffi.new('enum pfxv_state *')
        lib.lrtr_ip_str_to_addr(to_bytestr(prefix), lrtr_prefix)

        lib.rtr_mgr_validate(self.rtr_manager_config,
                             asn,
                             lrtr_prefix,
                             mask_len,
                             result
                             )

        return PfxvState(result[0])

class PfxvState(Enum):
    valid = lib.BGP_PFXV_STATE_VALID
    not_found = lib.BGP_PFXV_STATE_NOT_FOUND
    invalid = lib.BGP_PFXV_STATE_INVALID

