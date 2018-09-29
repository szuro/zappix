from __future__ import print_function, unicode_literals, absolute_import, division
from zappix.dstream import Dstream
import json


class Get(object):

    def __init__(self, host, port=10050, source_address=None):
        super().__init__(host, port, source_address)

    def get_value(self, key):
        pass

    def get_report(self, keys):
        pass