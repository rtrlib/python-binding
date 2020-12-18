# -*- coding:utf8 -*-
"""
rtrlib-python - a cffi based rtrlib wrapper

:license: MIT, see LICENSE for more details.
"""

from __future__ import absolute_import, unicode_literals

import logging

from .pfx_table import PfxTable
from .rtr_manager import RTRManager, PfxvState
from .manager_group import ManagerGroupStatus

logging.getLogger(__name__).addHandler(logging.NullHandler())

__version__ = 0.1
