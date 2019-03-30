import unittest
from ast import literal_eval
from zappix.protocol import ItemData


class TestItemData(unittest.TestCase):
    def test_init_without_clock(self):
        item = ItemData('testhost', 'testkey', 1)
        item_repr = str(item)
        d = {"host": "testhost", "key": "testkey", "value": 1}
        self.assertDictEqual(literal_eval(item_repr), d)

    def test_init_with_clock(self):
        item = ItemData('testhost', 'testkey', 1, 1553980979)
        item_repr = str(item)
        d = {"host": "testhost", "key": "testkey", "value": 1, "clock": 1553980979}
        self.assertDictEqual(literal_eval(item_repr), d)
