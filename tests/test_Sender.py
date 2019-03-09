import unittest
from unittest.mock import patch, MagicMock
from zappix.sender import Sender


class TestSender(unittest.TestCase):
    def setUp(self):
        self.msock = MagicMock()

    def test_init(self):
        get = Sender('host')
        self.assertEqual(get._port, 10051)
        self.assertIsNone(get._source_address)

        get = Sender('host', source_address='localhost')
        self.assertEqual(get._source_address, 'localhost')

    @patch('zappix.dstream.socket')
    def test_get_value(self, mock_socket):
        mock_socket.create_connection.return_value = self.msock
        self.msock.recv.side_effect = [
            b'ZBXD\x01', b'\x5b\x00\x00\x00\x00\x00\x00\x00',
            b'{"response":"success", "info":"processed: 1; failed: 0; total: 1; seconds spent: 0.060753"}', b''
            ]

        s = Sender('localhost')
        result = s.send_value('testhost', 'test', 1)

        self.assertIsNotNone(result.pop("seconds spent"))
        self.assertDictEqual(result, {"processed": 1, "failed": 0, "total": 1})
