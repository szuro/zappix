import socket
import json


class Get(object):

    def __init__(self, host, port=10050, source_address=None):
        self._host = host
        self._port = port
        self._source_address = source_address

    def get_value(self, key):
        pass

    def get_report(self, keys):
        pass