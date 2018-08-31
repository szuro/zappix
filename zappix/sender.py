"""
Python implementation of Zabbix sender.
"""

from __future__ import print_function, unicode_literals, absolute_import
import socket
import argparse
import json
from copy import deepcopy


class sender(object):

    _container = {"request": "sender data", "data": []}

    def __init__(self, ip, port=10051):
        self.ip = ip
        self.port = port

    def send_value(self, host, key, value):
        payload = {
            "host": host,
            "key": key,
            "value": value
        }

        full_crate = json.dumps(
                self._pack_payload(payload)
            ).encode('utf_8')
        return self._send(full_crate)

    def _pack_payload(self, payload):
        crate = deepcopy(self._container)
        crate['data'].append(payload)
        return crate

    def _send(self, payload):
        data = b""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self.ip, self.port))
            s.send(payload)
            data = s.recv(256)
            return data.decode("utf_8")

    def create_single_request(self, host, key, value):
        container = {"request": "sender data", "data": []}
        payload = {"host": host, "key": key, "value": value}
        container['data'].append(payload)

        return json.dumps(container).encode('utf_8')


if __name__ == '__main__':
    params = argparse.ArgumentParser()
    params.add_argument('-z', '--zabbix', nargs='?')
    params.add_argument('-p', '--port', nargs='?', default=10051, type=int)
    params.add_argument('-s', '--host', nargs='?')
    params.add_argument('-k', '--key', nargs='?')
    params.add_argument('-o', '--value', nargs='?')
    args = params.parse_args()

    zab = sender(args.zabbix, args.port)
    zab.send_value(args.host, args.key, args.value)
