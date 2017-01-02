Callbacks
=========

Rtrlib provides 3 callbacks one for updates on the manager status,
one for pfx_table and one for spki_table updates.

RTR Manager Status Callback
---------------------------

This callback is called when the RTR Managers status is changed.
The callback function must take 4 arguments.

.. function:: manager_status_callback(rtr_mgr_group, group_status, rtr_socket, data)

   :param rtr_mgr_group: socket group where the status change originates
   :param group_status: the new status
   :param rtr_socket: the socket where the change originates
   :param data: Data Object, if defined at manager initialization
   :type data: object or none

This callback is registered at manager initialization using status_callback parameter.
The data object may be passed with the status_callback_data parameter.

.. warning:: You should **not** register more than one function per callback for the following callbacks, it will **not** work and result in undefined behaviour


PFX update callback
-------------------

This callback is called for any change to the Prefix validation table, it takes two arguments.

.. function:: pfx_update_callback(pfx_record, added):

    :param pfx_record: The affected pfx record
    :type pfx_record: :class:`rtrlib.records.PFXRecord`
    :param added: Indicates whether the record was added or removed
    :type added: :class:`bool`

This callback can be registered using the :func:`rtrlib.register_pfx_update_callback` function

.. autofunction:: rtrlib.register_pfx_update_callback


SPKI update callback
--------------------

This callback is called for any change to the Subject Public Key Info table, it takes two arguments.

.. function:: spki_update_callback(spki_record, added):

    :param spki_record: The affected spki record
    :type spki_record: :class:`rtrlib.records.PFXRecord`
    :param added: Indicates whether the record was added or removed
    :type added: :class:`bool`

This callback can be registered using the :func:`rtrlib.register_spki_update_callback` function

.. autofunction:: rtrlib.register_spki_update_callback
