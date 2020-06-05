"""
Module containing handlers for Zabbix protocol.
"""

from typing import Optional
import abc
import socket
import struct


class _Dstream(abc.ABC):
    def __init__(self, target: str, port: int = 10051, source_address: Optional[str] = None) -> None:
        self._ip = target
        self._port = port
        self._source_address = source_address

    def _send(self, payload: bytes) -> str:
        data = b""
        parsed = ""
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

    def _parse_response(self, response: bytes) -> str:
        _, length = struct.unpack('<5sQ', response[:13])
        data = struct.unpack(
            '<{}s'.format(length),
            response[13:13+length]
            )[0]

        return data.decode('utf-8')

    def _prepare_payload(self, payload: bytes) -> bytes:
        packed = struct.pack(
            '<5sQ{}s'.format(len(payload)),
            b'ZBXD\x01',
            len(payload),
            payload
            )
        return packed

    def _recv_info(self, socket_: socket.socket, buff: int = 1024) -> bytes:
        data = b""
        buffer = socket_.recv(buff)
        while buffer:
            data += buffer
            buffer = socket_.recv(buff)
        return data
