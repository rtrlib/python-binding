#!/usr/bin/env python
# -*- coding: utf8 -*-

import argparse
import signal

from rtrlib import RTRManager, register_pfx_update_callback, register_spki_update_callback

def pfx_callback(pfx_record, added):
    if added:
        c = '+'
    else:
        c = '-'

    print("{sign} {prefix:40} {max:3} - {min:3} {asn:10}".format(
                    sign=c,
                    prefix=pfx_record.prefix,
                    max=pfx_record.max_len,
                    min=pfx_record.min_len,
                    asn=pfx_record.asn
                )
    )

def spki_callback(spki_table, spki_record, added):
    if added:
        c = '+'
    else:
        c = '-'

    print("{sign} {asn}".format(sign=c, asn=spki_record.asn))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("protocol", choices=('tcp', ))
    parser.add_argument("hostname")
    parser.add_argument("port", type=int)
    parser.add_argument(
                        "-k",
                        default=False,
                        action="store_true",
                        help="Print information about SPKI updates"
                        )
    parser.add_argument(
                        "-p",
                        default=False,
                        action="store_true",
                        help="Print information about PFX updates"
                        )
    args = parser.parse_args()

    if args.p:
        register_pfx_update_callback(pfx_callback)

    if args.k:
        register_spki_update_callback(spki_callback)

    print("{:40}   {:3}   {:4}".format("Prefix", "Prefix Length", "ASN"))
    with RTRManager(args.hostname, args.port) as mgr:
        try:
            signal.pause()
        except KeyboardInterrupt:
            pass

if __name__ == '__main__':
    main()
