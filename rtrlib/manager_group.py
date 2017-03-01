# -*- coding:utf8 -*-
"""
rtrlib.manager_group
--------------------

"""


from __future__ import absolute_import, unicode_literals
from enum import Enum

from _rtrlib import lib
from .rtr_socket import RTRSocketList


class ManagerGroup(object):
    """
    Wrapper around the rtr_mgr_group struct

    :param cdata group: A rtr_mgr_group struct
    """

    def __init__(self, group):
        self._group = group

    @property
    def preference(self):
        """
        The preference value of the group
        """
        return self._group.preference

    @property
    def sockets_len(self):
        """
        The sockets_len value of the group
        """
        return self._group.sockets_len

    @property
    def status(self):
        """
        The group status as enum34
        """
        return ManagerGroupStatus(self._group.status)

    @property
    def sockets(self):
        """
        The socket list as RTRSocketList
        """
        return RTRSocketList(self._group.sockets, self.sockets_len)


class ManagerGroupStatus(Enum):
    """Wrapper around the C enum rtr_mgr_status."""

    CLOSED = lib.RTR_MGR_CLOSED
    """RTR sockets are disconnected"""

    CONNECTING = lib.RTR_MGR_CONNECTING
    """RTR sockets trying to establish a connection"""
    ESTABLISHED = lib.RTR_MGR_ESTABLISHED
    """All RTR sockets of the group are synchronized with the rtr servers"""

    ERROR = lib.RTR_MGR_ERROR
    """Error occured on at least one RTR socket"""
