# -*- coding: utf8 -*-
"""
rtrlib.util
-----------

Utility functions and wrapper
"""

from __future__ import absolute_import, unicode_literals

import logging
import six
import threading

from six.moves import queue

from _rtrlib import ffi, lib
from .exceptions import IpConversionException


LOG = logging.getLogger(__name__)


def ip_str_to_addr(ip_str):
    """
    Convert an IP from string to rtrlib internal representation.

    :param str ip_str: IP address IPv4 and IPv6 are supported
    :return The IP address as cdata struct lrtr_ip_addr
    """
    addr = ffi.new('struct lrtr_ip_addr *')
    ret = lib.lrtr_ip_str_to_addr(to_bytestr(ip_str), addr)

    if ret != 0:
        raise IpConversionException("String could not be converted")

    return addr


def ip_addr_to_str(ip_addr):
    """
    Convert an IP from rtrlib internal to string representation.

    :param cdata ip_addr: IP address as cdata struct lrtr_ip_addr
    :return IP address as string
    """
    ip_str = ffi.new('char[]', 128)
    ret = lib.lrtr_ip_addr_to_str(ip_addr, ip_str, 128)

    if ret != 0:
        raise IpConversionException("ip_addr object could not be converted")
    return to_unicodestr(ffi.string(ip_str))


def to_bytestr(string):
    """If input string is a Unicode string convert to byte string."""
    if isinstance(string, six.text_type):
        return string.encode('utf8')
    return string


def to_unicodestr(string):
    """If input string is a byte string convert to Unicode string."""
    if isinstance(string, six.binary_type):
        return string.decode('utf8')

    return string


def is_integer(var):
    """Check if var is an integer."""
    return isinstance(var, six.integer_types)


def is_string(var):
    """Check if var is a string."""
    return isinstance(var, six.string_types)


class StoppableThread(threading.Thread):
    """
    Thread class with a stop() method.

    The thread itself has to check regularly for the stopped() condition.
    """

    def __init__(self, *args, **kwargs):
        super(StoppableThread, self).__init__(*args, **kwargs)
        self._stop_event = threading.Event()

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.isSet()


class CallbackGenerator(object):

    def __init__(self, function, callback, args=()):
        def inner_callback(pfx_record, data):
            while not data.thread.stopped():
                try:
                    data.callback(pfx_record, data.queue)
                    break
                except queue.Full:
                    pass
            return

        self.callback = callback
        self.queue = queue.Queue()
        new_args = list(args)
        new_args.extend((inner_callback, self))
        self.thread = StoppableThread(
                                      target=function,
                                      args=new_args,
                                      )
        self.thread.daemon = True

        self.thread.start()

    def __del__(self,):
        self.thread.stop()

    def __iter__(self,):
        return self

    def __next__(self,):
        while(True):
            try:
                LOG.debug('About to take item out of queue')
                item = self.queue.get_nowait()
                LOG.debug('Took "%s" out of the queue', item)
                self.queue.task_done()
                return item
            except queue.Empty:
                if self.thread.is_alive() or self.queue.qsize() > 0:
                    LOG.debug('Queue not yet filled, looping')
                    continue
                else:
                    LOG.debug('Queue empty stopping iteration')
                    raise StopIteration()

    def next(self,):
        return self.__next__()
