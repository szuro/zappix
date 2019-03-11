import unittest
import tempfile
import os
import random
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

    @patch('zappix.dstream.socket')
    def test_send_file(self, mock_socket):
        file_ = tempfile.NamedTemporaryFile('w+', delete=False)
        file_.write("testhost test 1\n"
                    "testhost test  2\n"
                    "testhost test   3\n")
        file_.close()
        mock_socket.create_connection.return_value = self.msock
        self.msock.recv.side_effect = [
            b'ZBXD\x01', b'\x5b\x00\x00\x00\x00\x00\x00\x00',
            b'{"response":"success", "info":"processed: 3; failed: 0; total: 3; seconds spent: 0.060753"}', b''
            ]

        sender = Sender('localhost')
        resp, _ = sender.send_file(file_.name)
        os.unlink(file_.name)
        self.assertIsNotNone(resp.pop("seconds spent"))
        self.assertDictEqual(resp, {"processed": 3, "failed": 0, "total": 3})

    @patch('zappix.dstream.socket')
    def test_send_decorator(self, mock_socket):
        mock_socket.create_connection.return_value = self.msock
        self.msock.recv.side_effect = [
            b'ZBXD\x01', b'\x5b\x00\x00\x00\x00\x00\x00\x00',
            b'{"response":"success", "info":"processed: 1; failed: 0; total: 1; seconds spent: 0.060753"}', b''
            ]

        sender = Sender('host')

        @sender.send_result('testhost', 'test')
        def echo(number):
            return number

        number = random.randint()
        res = echo(number)
        self.assertEqual(res, number)
