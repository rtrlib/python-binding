.. _Usage Examples:

Usage Examples
==============

Validation
----------

::

    from rtrlib import RTRManager, PfxvState

    mgr = RTRManager('rpki-validator.realmv6.org', 8282)
    mgr.start()
    result = mgr.validate(12345, '10.10.0.0', 24)

    if result == PfxvState.valid:
        print('Prefix Valid')
    elif result == PfxvState.invalid:
        print('Prefix Invalid')
    elif result == PfxvState.not_found:
        print('Prefix not found')
    else:
        print('Invalid response')

    mgr.stop()


PFX Table iteration (with iterator)
-----------------------------------

::

    from rtrlib import RTRManager, PfxvState

    mgr = RTRManager('rpki-validator.realmv6.org', 8282)
    mgr.start()
    result = mgr.validate(12345, '10.10.0.0', 24)

    for recordv4 in mgr.ipv4_records():
        print(recordv4)

    mgr.stop()


PFX Table iteration (with callback)
-----------------------------------

::

    from rtrlib import RTRManager, PfxvState

    def callback(pfx_record, data):
        print(pfx_record)

    mgr = RTRManager('rpki-validator.realmv6.org', 8282)
    mgr.start()
    result = mgr.validate(12345, '10.10.0.0', 24)

    mgr.for_each_ipv4_record(callback, None)

    mgr.stop()


Print PFX updates
-----------------

::

    from rtrlib import RTRManager

    def callback(pfx_record, added, data):
        print('%s %s' % ('+' if added else '-', pfx_record))

    mgr = RTRManager('rpki-validator.realmv6.org', 8282, pfx_update_callback=callback)
    mgr.start()

    mgr.stop()


Advanced Usage
--------------
.. note:: This is by no means supposed to be a reference on cffi itself, \
    if you want to do something like this please read the cffi_ Documentation.

I case you want to do something that is not (yet) supported by the binding \
you can access the c functions directly.

Let's say you implemented RFC6810 yourself but still want to use rtrlibs pfxtable.

::

    # _rtrlib is the cffi object, it contains the actual bindings in lib
    # and helper functions for allocation and
    # other stuff that is not native to python
    from _rtrlib import lib, ffi

    # only imported for the pfx_table_callback
    import rtrlib

    # allocate pfx_table
    pfx_table = ffi.new('struct pfx_table *')

    # initialize it
    lib.pfx_table_init(pfx_table, ffi.NULL)


    def add_record(asn, ip, prefixmin, prefixmax):
        record = ffi.new('struct pfx_record *')
        prefix = ffi.new('struct lrtr_ip_addr *')
        lib.lrtr_ip_str_to_addr(ip.encode('ascii'), prefix)

        record.asn = asn
        record.min_len = prefixmin
        record.max_len = prefixmax
        record.socket = ffi.NULL
        record.prefix = prefix[0]

        lib.pfx_table_add(pfx_table, record)

    # add records
    records = ((234, '22.45.66.0', 24, 24),
               (545, '9..0.0', 8, 8),
               (4545, '223.4.66.0', 24, 24),
               (5454, '120.6.47.0', 24, 24))

    for record in records:
        asn, ip, min_len, max_len = record
        add_record(asn, ip, min_len, max_len)


    # iterate over pfx_table to demonstrate it's content

    # since the callback from the rtrlib module is used record
    # is automatically wrapped in a python class
    def callback(record, notused):
        print(record)

    # necessary because cffi new style callbacks are used,
    # lib.pfx_table_callback is a wrapper that calls the actual callback
    handle = ffi.new_handle((callback, None))

    lib.pfx_table_for_each_ipv4_record(pfx_table, lib.pfx_table_callback, handle)

    lib.pfx_table_free(pfx_table)



.. _cffi: https://cffi.readthedocs.io/en/latest/
