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
-------------------

::

    from rtrlib import RTRManager, register_pfx_update_callback

    def callback(pfx_record, added):
        print('%s %s' % ('+' if added else '-', pfx_record))

    register_pfx_update_callback(callback)

    mgr = RTRManager('rpki-validator.realmv6.org', 8282)
    mgr.start()

    mgr.stop()

