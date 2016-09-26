
from cffi import FFI
from os import path


BASEDIR = path.dirname(path.realpath(__file__))


ffibuilder = FFI()

ffibuilder.set_source("rtrlib._rtrlib",
                      """
                      #include <rtrlib/rtrlib.h>
                      """,
                      libraries=['rtr'])


with open(path.join(BASEDIR, "rtrlib.cdef")) as file_obj:
    ffibuilder.cdef(file_obj.read())

ffibuilder.cdef("""
        extern "Python" void rtr_mgr_status_callback(const struct rtr_mgr_group *, enum rtr_mgr_status, const struct rtr_socket *, void *);
        extern "Python" void pfx_update_callback(struct pfx_table *pfx_table, const struct pfx_record record, const bool added);
        extern "Python" void spki_update_callback(struct spki_table *spki_table, const struct spki_record record, const bool added);
                """)

if __name__ == "__main__":
    ffibuilder.compile(verbose=True)
