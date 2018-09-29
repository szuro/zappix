from __future__ import print_function, unicode_literals, absolute_import, division
import socket
import re
import json


class Dstream(object):
    def __init__(self, target, port=10051, source_address=None):
        self._ip = target
        self._port = port
        self._source_address = source_address

    def _send(self, payload):
        data = b""
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.connect((self._ip, self._port))
            if self._source_address:
                s.bind((self._source_address, 0))
            # for item in payload:
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