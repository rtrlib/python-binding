# -*- coding:utf8 -*-

from __future__ import absolute_import, unicode_literals

from enum import Enum

from _rtrlib import lib

class RTRSocketList(object):

    def __init__(self, sockets, length):
        self._sockets = sockets
        self._length = length

    def __getitem__(self, key):
        print(key)
        if not isinstance(key, int):
            raise TypeError("Index must be int")
        if key >= self._length:
            raise IndexError("Index out of range")
        elif key < 0:
            raise IndexError("Index may not be negative")
        return RtrSocket(self._sockets[key])


class RTRSocket(object):

    def __init__(self, socket):
        self._socket = socket

    @property
    def expire_interval(self):
        return self._socket.expire_interval

    @property
    def has_recieved_pdus(self):
        return self._socket.has_recieved_pdus

    @property
    def last_update(self):
        return self._socket.last_update

    @property
    def refresh_interval(self):
        return self._socket.refresh_interval

    @property
    def retry_interval(self):
        return self._socket.retry_interval

    @property
    def state(self):
        return RtrSocketState(self._socket.state)

    @property
    def version(self):
        return self._socket.version


class RtrSocketState(Enum):
    CONNECTING = lib.RTR_CONNECTING
    ESTABLISHED = lib.RTR_ESTABLISHED
    RESET = lib.RTR_RESET
    SYNC = lib.RTR_SYNC
    FAST_RECONNECT = lib.RTR_FAST_RECONNECT
    ERROR_NO_DATA_AVAILABLE = lib.RTR_ERROR_NO_DATA_AVAIL
    ERROR_NO_INCREMENTAL_UPDATE_AVAILABLE = lib.RTR_ERROR_NO_INCR_UPDATE_AVAIL
    ERROR_FATAL = lib.RTR_ERROR_FATAL
    ERROR_TRANSPORT = lib.RTR_ERROR_TRANSPORT
    SHUTDOWN = lib.RTR_SHUTDOWN
