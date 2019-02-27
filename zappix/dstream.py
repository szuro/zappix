"""
Module containing handlers for Zabbix protocol.
"""

import abc
import socket
import struct


class _Dstream(abc.ABC):
    def __init__(self, target, port=10051, source_address=None):
        self._ip = target
        self._port = port
        self._source_address = source_address

    def _send(self, payload):
        data = b""
        parsed = None
        s = None
        try:
            if self._source_address:
                s = socket.create_connection(
                    (self._ip, self._port),
                    source_address=(self._ip, 0))
            else:
                s = socket.create_connection((self._ip, self._port))
            packed = self._prepare_payload(payload)
            s.sendall(packed)
            data = self._recv_info(s)
            parsed = self._parse_response(data)
        except socket.error:
            print("Cannot connect to host.")
        except struct.error:
            print("Invalid response.")
        finally:
            if s:
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

    def _recv_info(self, socket_, buff=1024):
        data = b""
        buffer = socket_.recv(buff)
        while buffer:
            data += buffer
            buffer = socket_.recv(buff)
        return data
