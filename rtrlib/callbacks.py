# -*- coding:utf8 -*-
"""
Utility functions and wrapper for callbacks
"""
from __future__ import absolute_import, unicode_literals

import logging

from _rtrlib import ffi, lib
from .manager_group import ManagerGroup, ManagerGroupStatus
from .rtr_socket import RTRSocket
from .records import PFXRecord, SPKIRecord

LOG = logging.getLogger(__name__)

PFX_UPDATE_CALLBACK = ffi.NULL
SPKI_UPDATE_CALLBACK = ffi.NULL


def register_pfx_update_callback(func):
    """
    Register RTR manager pfx_update_callback

    :param function func: Callback function
    """
    global PFX_UPDATE_CALLBACK
    register_callback(
        pfx_update_callback_wrapper(func),
        "pfx_update_callback"
        )

    PFX_UPDATE_CALLBACK = lib.pfx_update_callback


def register_spki_update_callback(func):
    """
    Register RTR manager spki update callback

    .. warning:: This callback is untested, because at the time of writing
        no caching server with spki records was available.
        It should work but might cause you computer to explode.

    :param function func: Callback function
    """
    global SPKI_UPDATE_CALLBACK
    register_callback(
        spki_update_callback_wrapper(func),
        "spki_update_callback"
        )

    SPKI_UPDATE_CALLBACK = lib.spki_update_callback


def register_callback(callback, name):
    """
    Registers a cffi callback
    """
    LOG.debug('Registering callback %s', name)
    ffi.def_extern(name=name)(callback)


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


def pfx_update_callback_wrapper(func):
    """
    Wraps the given python function and wraps it to hide cffi specifics.
    This wrapper is only for the pfx update callback of the rtrlib manager.
    """
    def inner(pfx_table, pfx_record, added):
        """
        Hides c structures
        """
        LOG.debug("Calling pfx update callback")
        func(
            PFXRecord(pfx_record),
            added,
            )
    return inner


def spki_update_callback_wrapper(func):
    """
    Wraps the given python function and wraps it to hide cffi specifics.
    This wrapper is only for the spki update callback of the rtrlib manager.
    """
    def inner(record, added):
        """
        Hides c structures
        """
        LOG.debug("Calling spki update callback")
        func(
            SPKIRecord(record),
            added,
            )
    return inner
