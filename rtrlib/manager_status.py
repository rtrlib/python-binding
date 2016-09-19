# -*- coding:utf8 -*-

from __future__ import absolute_import, unicode_literals

from enum import Enum
from _rtrlib import ffi,lib

from .util import *


class ManagerStatus(Enum):
    CLOSED = lib.RTR_MGR_CLOSED
    CONNECTING = lib.RTR_MGR_CONNECTING
    ESTABLISHED = lib.RTR_MGR_ESTABLISHED
    ERROR = lib.RTR_MGR_ERROR

    @property
    def message(self):
        return to_unicodestr(ffi.string(lib.rtr_mgr_status_to_str(self.value)))
