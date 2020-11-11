# -*- coding:utf8 -*-
"""
Utility functions and wrapper for callbacks
"""
from __future__ import absolute_import, unicode_literals

import logging

from _rtrlib import ffi
from .manager_group import ManagerGroup, ManagerGroupStatus
from .rtr_socket import RTRSocket
from .records import PFXRecord, SPKIRecord

LOG = logging.getLogger(__name__)


@ffi.def_extern(name="rtr_mgr_status_callback")
def status_callback(rtr_mgr_group, group_status, rtr_socket, object_handle):
    """
    Wraps the given python function and wraps it to hide cffi specifics.
    This wrapper is only for the status callback of the rtrlib manager.
    """

    object_ = ffi.from_handle(object_handle)

    object_._status_callback(
        ManagerGroup(rtr_mgr_group),
        ManagerGroupStatus(group_status),
        RTRSocket(rtr_socket),
        object_._status_callback_data
        )


@ffi.def_extern(name="pfx_table_callback")
def pfx_table_callback(pfx_record, object_handle):
    """
    Wraps the pfx_table callback, used for iteration of the pfx table,
    to hide cffi specifics
    """
    callback, data = ffi.from_handle(object_handle)

    callback(PFXRecord(pfx_record), data)


@ffi.def_extern(name="pfx_update_callback")
def pfx_update_callback(pfx_table, record, added):
    wrapped_socket = ffi.cast("struct rtr_socket_wrapper *", record.socket)
    mgr = ffi.from_handle(wrapped_socket.data)

    mgr._pfx_update_callback(
            PFXRecord(record),
            added,
            mgr._pfx_update_callback_data,
        )


@ffi.def_extern(name="spki_update_callback")
def spki_update_callback(spki_table, record, added):
    wrapped_socket = ffi.cast("struct rtr_socket_wrapper *", record.socket)
    mgr = ffi.from_handle(wrapped_socket.data)

    mgr._spki_update_callback(
            SPKIRecord(record),
            added,
            mgr._spki_update_callback_data,
            )
