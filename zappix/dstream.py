"""
Module containing handlers for Zabbix protocol.
"""

from typing import Optional
import abc
import socket
import struct
import logging

logger = logging.getLogger(__name__)


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
                    source_address=(self._source_address, 0))
                logger.info(f"Opening connection to {self._ip}:{self._port} with source address {self._source_address}")
            else:
                s = socket.create_connection((self._ip, self._port))
                logger.info(f"Opening connection to {self._ip}:{self._port}")
            packed = self._prepare_payload(payload)
            s.sendall(packed)
            data = self._recv_info(s)
            parsed = self._parse_response(data)
        except socket.error:
            logger.exception(f"Cannot connect to host {self._ip}:{self._port}:")
        except struct.error:
            logger.exception(f"Recived response is corrupted:")
        finally:
            if s:
                logger.info(f"Closing connection to {self._ip}:{self._port}")
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
        payload_len = len(payload)
        packed = struct.pack(
            '<5sQ{}s'.format(payload_len),
            b'ZBXD\x01',
            payload_len,
            payload
            )
        logger.debug(f"Packed payload for {self._ip}:{self._port}. Payload length: {payload_len}. Length with headers: {len(packed)}")
        return packed

    def _recv_info(self, socket_: socket.socket, buff: int = 1024) -> bytes:
        data = b""
        buffer = socket_.recv(buff)
        logger.debug(f"Received {len(buffer)} from {self._ip}:{self._port}")
        while buffer:
            data += buffer
            buffer = socket_.recv(buff)
            logger.debug(f"Received {len(buffer)} from {self._ip}:{self._port}")
        logger.debug(f"Completed data retrieval from {self._ip}:{self._port}. Total length: {len(data)}")
        return data
