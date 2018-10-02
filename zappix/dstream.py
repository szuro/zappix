from __future__ import print_function, unicode_literals, absolute_import, division
import socket
import struct


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
            packed = self._prepare_payload(payload)
            s.sendall(packed)
            data = s.recv(256)
            parsed = self._parse_response(data)
        except socket.error:
            print("Cannot connect to host.")
            parsed = None
        finally:
            s.close()
            return parsed

    def _parse_response(self, response):
        _, length = struct.unpack('<5sQ', response[:13])
        data = struct.unpack(
            '<{}s'.format(length),
            response[13:13+length]
            )
        return data[0].decode('utf-8')

    def _prepare_payload(self, payload):
        packed = struct.pack(
            '<5sQ{}s'.format(len(payload)),
            b'ZBXD\x01',
            len(payload),
            payload
            )
        return packed