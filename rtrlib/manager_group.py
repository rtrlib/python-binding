# -*- coding:utf8 -*-

from __future__ import absolute_import, unicode_literals

from .rtr_socket import RTRSocket, RTRSocketList
from .manager_status import ManagerStatus

class ManagerGroup(object):

    def __init__(self, group):
        self._group = group

    @property
    def preference(self):
        return self._group.preference

    @property
    def sockets_len(self):
        return self._group.sockets_len

    @property
    def status(self):
        return ManagerStatus(self._group.status)

    @property
    def sockets(self):
        return RtrSocketList(self._group.sockets, self.sockets_len)
