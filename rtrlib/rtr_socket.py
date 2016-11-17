# -*- coding:utf8 -*-
"""
rtrlib.rtr_socket
-----------------
"""

from __future__ import absolute_import, unicode_literals

from enum import Enum

from _rtrlib import lib


class RTRSocketList(object):
    """
    List of RTRSockets. Can be accessed like any other list.

    Read Only.
    """

    def __init__(self, sockets, length):
        self._sockets = sockets
        self._length = length

    def __getitem__(self, key):
        if not isinstance(key, int):
            raise TypeError("Index must be int")
        if key >= self._length:
            raise IndexError("Index out of range")
        elif key < 0:
            raise IndexError("Index may not be negative")
        return RTRSocket(self._sockets[key])


class RTRSocket(object):
    """
    Wrapper around the rtr_socket struct

    :param cdata socket: rtr_socket struct
    """

    def __init__(self, socket):
        self._socket = socket

    @property
    def expire_interval(self):
        """
        Time period in seconds.
        Received records are deleted if the client was unable to refresh \
        data for this time period. If 0 is specified, the expire_interval \
        is twice the refresh_interval.
        """
        return self._socket.expire_interval

    @property
    def has_recieved_pdus(self):
        """
        True, if this socket has already received PDUs
        """
        return self._socket.has_recieved_pdus

    @property
    def last_update(self):
        """
        Timestamp of the last validation record update.
        Is 0 if the pfx_table doesn't stores any validation records from this \
        rtr_socket.
        """
        return self._socket.last_update

    @property
    def refresh_interval(self):
        """
        Time period in seconds.
        Tells the router how long to wait before next attempting \
        to poll the cache, using a Serial Query or Reset Query PDU.
        """
        return self._socket.refresh_interval

    @property
    def retry_interval(self):
        """
        Time period in seconds between a failed query and the next attempt.
        """
        return self._socket.retry_interval

    @property
    def state(self):
        """
        Current state of the socket.
        """
        return RTRSocketState(self._socket.state)

    @property
    def version(self):
        """
        Protocol version used by this socket
        """
        return self._socket.version


class RTRSocketState(Enum):
    """
    States of the RTR socket
    """

    CONNECTING = lib.RTR_CONNECTING
    """Socket is establishing the transport connection"""

    ESTABLISHED = lib.RTR_ESTABLISHED
    """
    Connection is established and socket is waiting for a Serial Notify or \
    expiration of the refresh_interval timer.
    """

    RESET = lib.RTR_RESET
    """Resetting RTR connection"""

    SYNC = lib.RTR_SYNC
    """Receiving validation records from the RTR server"""

    FAST_RECONNECT = lib.RTR_FAST_RECONNECT
    """Reconnect without any waiting period"""

    ERROR_NO_DATA_AVAILABLE = lib.RTR_ERROR_NO_DATA_AVAIL
    """No validation records are available on the RTR server"""

    # pylint: disable=invalid-name
    ERROR_NO_INCREMENTAL_UPDATE_AVAILABLE = lib.RTR_ERROR_NO_INCR_UPDATE_AVAIL
    """Server was unable to answer the last serial or reset query"""

    ERROR_FATAL = lib.RTR_ERROR_FATAL
    """Fatal protocol error occurred"""

    ERROR_TRANSPORT = lib.RTR_ERROR_TRANSPORT
    """Error on the transport socket occurred"""

    SHUTDOWN = lib.RTR_SHUTDOWN
    """RTR Socket is stopped"""
