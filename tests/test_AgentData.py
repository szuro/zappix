import unittest
from ast import literal_eval
from zappix.protocol import AgentData


class TestItemData(unittest.TestCase):
    def test_basic_init(self):
        item = AgentData('testhost', 'testkey', 1, 1553980979, 1000)
        item_repr = str(item)
        d = {"host": "testhost", "key": "testkey", "value": 1, "clock": 1553980979, "ns": 1000}
        self.assertDictEqual(literal_eval(item_repr), d)
