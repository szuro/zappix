import unittest
from ast import literal_eval
from zappix.protocol import ActiveChecksRequest


class TestActiveChecksRequest(unittest.TestCase):
    def test_basic_init(self):
        item = ActiveChecksRequest('testhost')
        item_repr = str(item)
        d = {"host": "testhost", "request": "active checks"}
        self.assertDictEqual(literal_eval(item_repr), d)
