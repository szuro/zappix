"""
Python implementation of Zabbix sender.
"""

from __future__ import print_function, unicode_literals, absolute_import
import socket
import json
import re
from copy import deepcopy


class Sender(object):

    _container = {"request": "sender data", "data": []}

    def __init__(self, ip, port=10051):
        self._ip = ip
        self._port = port

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
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.connect((self._ip, self._port))
            s.sendall(payload)
            data = s.recv(256)
        except socket.error:
            print("Cannot connect to host.")
        finally:
            s.close()
            return self._parse_response(data.decode("utf_8"))

    def _parse_response(self, response):
        resp = re.search('{.*}', response).group()
        return json.loads(resp)


if __name__ == '__main__':
    import argparse
    params = argparse.ArgumentParser()
    params.add_argument('-z', '--zabbix', nargs='?')
    params.add_argument('-p', '--port', nargs='?', default=10051, type=int)
    params.add_argument('-s', '--host', nargs='?')
    params.add_argument('-k', '--key', nargs='?')
    params.add_argument('-o', '--value', nargs='?')
    args = params.parse_args()

    zab = Sender(args.zabbix, args.port)
    result = zab.send_value(args.host, args.key, args.value)
    print('info from server: "{}"'.format(result['info']))
