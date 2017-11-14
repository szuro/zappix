"""
Python implementation of Zabbix sender.
"""

from __future__ import print_function, unicode_literals, absolute_import
import socket
import argparse


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
        except ConnectionRefusedError:
            print("Cannot connect to host.")
        finally:
            s.close()


if __name__ == '__main__':
    params = argparse.ArgumentParser()
    params.add_argument('-z', '--zabbix', nargs=1)
    params.add_argument('-p', '--port', nargs='?', default=10051, type=int)
    params.add_argument('-s', '--host', action="store_true")
    params.add_argument('-k', '--key', action="store_true")
    params.add_argument('-o', '--value', action="store_true")
    args = params.parse_args()

