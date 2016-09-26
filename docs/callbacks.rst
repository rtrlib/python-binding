Callbacks
=========

The rtrlib provides 3 callbacks one for updates on the manager status,
one for pfx_table and one for spki_table updates.

.. warning:: You should **not** register more than one function per callback, it will not work and result in undefined behaviour

.. autofunction:: rtrlib.register_status_callback
.. autofunction:: rtrlib.register_pfx_update_callback
.. autofunction:: rtrlib.register_spki_update_callback
