"""
rtrlib-python - a cffi based rtrlib wrapper
"""

from __future__ import absolute_import, unicode_literals

import logging

from .rtr_manager import RTRManager


logging.getLogger(__name__).addHandler(logging.NullHandler())
