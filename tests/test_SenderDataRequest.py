import unittest
from ast import literal_eval
from zappix.protocol import SenderData, SenderDataRequest


class TestSenderDataRequest(unittest.TestCase):
    def setUp(self):
        self.empty_sender = {"request": "sender data"}
        self.sender_with_data = {"request": "sender data", "data": [
                {"host": "testhost", "key": "testkey", "value": 1}
            ]}

    def test_basic_init(self):
        sender_request = SenderDataRequest()
        self.assertIsInstance(sender_request, SenderDataRequest)
        self.assertDictEqual(
            literal_eval(str(sender_request)),
            self.empty_sender
            )

    def test_init_with_data(self):
        sender_request = SenderDataRequest([SenderData('testhost', 'testkey', 1)])
        self.assertIsInstance(sender_request, SenderDataRequest)
        self.assertDictEqual(
            literal_eval(str(sender_request)),
            self.sender_with_data
            )

    def test_init_with_invalid_data(self):
        with self.assertRaises(ValueError):
            SenderDataRequest([('testhost', 'testkey', 1)])

    def test_add_item(self):
        sender_request = SenderDataRequest()
        self.assertDictEqual(
            literal_eval(str(sender_request)),
            self.empty_sender
            )
        sender_request.add_item(SenderData('testhost', 'testkey', 1))
        self.assertDictEqual(
            literal_eval(str(sender_request)),
            self.sender_with_data
            )

    def test_add_invalid_item(self):
        with self.assertRaises(ValueError):
            sender_request = SenderDataRequest()
            sender_request.add_item(('testhost', 'testkey', 1))
