
from cffi import FFI
from os import path


BASEDIR = path.dirname(path.realpath(__file__))


ffibuilder = FFI()

ffibuilder.set_source("_rtrlib",
                      """
                      #include <rtrlib/rtrlib.h>
                      """,
                      libraries=['rtr'])


with open(path.join(BASEDIR, "rtrlib.cdef")) as file_obj:
    ffibuilder.cdef(file_obj.read())


if __name__ == "__main__":
    ffibuilder.compile(verbose=True)
