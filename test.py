
from _rtrlib import ffi, lib

import weakref
import time



tr_tcp = ffi.new('struct tr_socket *')
rtr = ffi.new('struct rtr_socket []', 1)
tcp_config = ffi.new('struct tr_tcp_config *')
groups = ffi.new('struct rtr_mgr_group[]', 1)
confp = ffi.new('struct rtr_mgr_config **')


host = ffi.new('char[]', b'rpki-validator.realmv6.org')
port = ffi.new('char[]', b'8282')

tcp_config.host = host
tcp_config.port = port

lib.tr_tcp_init(tcp_config, tr_tcp)

rtr[0].tr_socket = tr_tcp

groups[0].sockets_len = 1
socketsp = ffi.new('struct rtr_socket **', rtr)
groups[0].sockets = socketsp
groups[0].preference = 1

print(lib.rtr_mgr_init(confp, groups, 1, 30, 600, 600, ffi.NULL, ffi.NULL, ffi.NULL, ffi.NULL))
conf = confp[0]

print(lib.rtr_mgr_start(conf))

while lib.rtr_mgr_conf_in_sync(conf) != 1:
    time.sleep(1)


result = ffi.new('enum pfxv_state *')
ip = ffi.new('struct lrtr_ip_addr *')
lib.lrtr_ip_str_to_addr(b'192.168.179.2', ip)

lib.rtr_mgr_validate(conf, 10, ip, 120, result)
print(result[0])


input()

lib.rtr_mgr_stop(conf)
lib.rtr_mgr_free(conf)
