"""
Python implementation of Zabbix sender.
"""

from __future__ import print_function, unicode_literals, absolute_import
import socket


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
