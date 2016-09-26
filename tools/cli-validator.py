#!/usr/bin/env python
# -*- coding: utf8 -*-

from __future__ import unicode_literals, print_function

import fileinput
import re
import sys

from time import sleep

from rtrlib import RTRManager, ManagerGroupStatus, register_status_callback

INPUT_REGEX = re.compile(
        r'^(?P<ip>[0-9a-fA-F.:]+) (?P<prefix>\d{1,3}) (?P<ASN>\d+)$'
    )

OUTPUT_FORMAT = "{}/{} {}: {}"

class GroupStatus(object):
    def __init__(self):
        self.error = False

def connection_status_collback(rtr_mgr_group, group_status, rtr_socket, data):
    if group_status == ManagerGroupStatus.ERROR:
        data.error = True

def main():
    if len(sys.argv) < 3:
        print("Usage: {} [host] [port]".format(sys.argv[0]))
        exit()

    register_status_callback(connection_status_collback)
    status = GroupStatus()
    mgr = RTRManager(
                     sys.argv[1],
                     sys.argv[2],
                     status_fp_data=status
                    )

    mgr.start()
    while not mgr.is_synced():
        sleep(0.2)
        if status.error:
            print("Connection error")
            exit()

    for line in fileinput.input('-'):
        line = line.strip()
        match  = INPUT_REGEX.match(line)
        if not match:
            print("Invalid line '%s'" % line)
            print("Arguments required: IP Mask ASN")
        else:
            asn = int(match.group('ASN'))
            ip = match.group('ip')
            prefix_length = int(match.group('prefix'))
            result = mgr.validate(asn, ip, prefix_length)
            print(OUTPUT_FORMAT.format(ip, prefix_length, asn, result))

    mgr.stop()


if __name__ == '__main__':
    main()
