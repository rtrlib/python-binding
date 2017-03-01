
from cffi import FFI
from os import path


BASEDIR = path.dirname(path.realpath(__file__))


ffibuilder = FFI()

with open(path.join(BASEDIR, "rtrlib.cdef")) as file_obj:
    ffibuilder.cdef(file_obj.read())

ffibuilder.cdef("""
        extern "Python" void rtr_mgr_status_callback(const struct rtr_mgr_group *, enum rtr_mgr_status, const struct rtr_socket *, void *);
        extern "Python" void pfx_update_callback(struct pfx_table *pfx_table, const struct pfx_record record, const bool added);
        extern "Python" void spki_update_callback(struct spki_table *spki_table, const struct spki_record record, const bool added);
        extern "Python" void pfx_table_callback(const struct pfx_record *pfx_record, void *data);
                """)

ffibuilder.cdef("""
                void free(void *ptr);
                """)

ffibuilder.set_source("_rtrlib",
                      """
                      #include <rtrlib/rtrlib.h>

                      /*
                       * check if ssh support is available
                       * if not define tr_ssh_config struct
                       * and have_ssh with return 0
                       * otherwise just define have_ssh with return 1
                       */
                      #ifndef RTRLIB_HAVE_LIBSSH
                      struct tr_ssh_config {
                          char *host;
                          unsigned int port;
                          char *bindaddr;
                          char *username;
                          char *server_hostkey_path;
                          char *client_privkey_path;
                      };
                      int have_ssh(void) {return 0;}
                      #endif

                      #ifdef RTRLIB_HAVE_LIBSSH
                      int have_ssh(void) {return 1;}
                      #endif
                      """,
                      libraries=['rtr'])

if __name__ == "__main__":
    ffibuilder.compile(verbose=True)
