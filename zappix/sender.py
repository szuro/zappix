"""
Python implementation of Zabbix sender.
"""

from __future__ import print_function, unicode_literals, absolute_import
import socket
import argparse
import json


class sender(object):
    def __init__(self, ip, port=10051):
        self.ip = ip
        self.port = port

    def send(self, payload):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((self.ip, self.port))
            s.send(payload)
            data = s.recv(124)
        except socket.error:
            print("Cannot connect to host.")
        finally:
            s.close()
    
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
    zab.send(zab.create_single_request(args.host, args.key, args.value))

