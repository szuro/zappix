import unittest
from unittest.mock import patch, MagicMock
from zappix.get import Get


class TestGet(unittest.TestCase):
    def setUp(self):
        self.msock = MagicMock()

    def test_init(self):
        get = Get('host')
        self.assertEqual(get._port, 10050)
        self.assertIsNone(get._source_address)

        get = Get('host', source_address='localhost')
        self.assertEqual(get._source_address, 'localhost')

    @patch('zappix.dstream.socket')
    def test_get_value(self, mock_socket):
        mock_socket.create_connection.return_value = self.msock
        self.msock.recv.side_effect = [
            b'ZBXD\x01', b'\x01\x00\x00\x00\x00\x00\x00\x00', b'1', b''
            ]

        g = Get('localhost')
        result = g.get_value('agent.ping')

        self.assertEqual(result, '1')

    @patch('zappix.dstream.socket')
    def test_get_report(self, mock_socket):
        mock_socket.create_connection.return_value = self.msock
        self.msock.recv.side_effect = [
            b'ZBXD\x01', b'\x01\x00\x00\x00\x00\x00\x00\x00', b'1', b'',
            b'ZBXD\x01', b'\x09\x00\x00\x00\x00\x00\x00\x00', b'localhost', b''
            ]

        g = Get('localhost')
        result = g.get_report(('agent.ping', 'system.hostname'))

        self.assertDictEqual(
            result,
            {'agent.ping': '1', 'system.hostname': 'localhost'}
        )


if __name__ == '__main__':
    unittest.main()
