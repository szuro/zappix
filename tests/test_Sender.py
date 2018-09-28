import unittest
import configparser
import os
import tempfile
from zappix.sender import Sender


class SenderValueTest(unittest.TestCase):
    def setUp(self):
        config = configparser.ConfigParser()
        this_path = os.path.dirname(os.path.abspath(__file__))
        config.read(os.path.join(this_path, 'test.ini'))
        self.server = config['server']['good']

        self.sender = Sender(self.server)

    def test_single_value(self):
        resp = self.sender.send_value('testhost','test', 1)
        self.assertIsNotNone(resp)
        self.assertIsNotNone(resp['info'])
        self.assertRegex(resp['info'], r"processed: 1; failed: 0; total: 1; seconds spent: [0-9]+.[0-9]+")

    def test_bad_value(self):
        resp = self.sender.send_value('testhost','test', "bad_value")
        self.assertIsNotNone(resp)
        self.assertIsNotNone(resp['info'])
        self.assertRegex(resp['info'], r"processed: 0; failed: 1; total: 1; seconds spent: [0-9]+.[0-9]+")

    def test_bad_key(self):
        resp = self.sender.send_value('testhost','bad_key', 1)
        self.assertIsNotNone(resp)
        self.assertIsNotNone(resp['info'])
        self.assertRegex(resp['info'], r"processed: 0; failed: 1; total: 1; seconds spent: [0-9]+.[0-9]+")

    def test_bad_hostname(self):
        resp = self.sender.send_value('bad_host','test', 1)
        self.assertIsNotNone(resp)
        self.assertIsNotNone(resp['info'])
        self.assertRegex(resp['info'], r"processed: 0; failed: 1; total: 1; seconds spent: [0-9]+.[0-9]+")

    @unittest.skip
    def test_bad_server(self):
        sender = Sender('127.0.0.2')
        resp = sender.send_value('testhost','test', 1)
        self.assertIsNotNone(resp)
        self.assertIsNotNone(resp['info'])

    @unittest.skip
    def test_bad_port(self):
        sender = Sender(self.server, 666)
        resp = sender.send_value('testhost','test', 1)
        self.assertIsNotNone(resp)
        self.assertIsNotNone(resp['info'])


class SenderFileTest(unittest.TestCase):
    def setUp(self):
        config = configparser.ConfigParser()
        this_path = os.path.dirname(os.path.abspath(__file__))
        config.read(os.path.join(this_path, 'test.ini'))
        self.server = config['server']['good']

        self.sender = Sender(self.server)
        self.file = os.path.join(this_path, 'test.csv')

    def test_send_file(self):
        resp = self.sender.send_file(self.file)
        self.assertIsNotNone(resp)
        self.assertIsNotNone(resp['info'])
        self.assertRegex(resp['info'], r"processed: [0-9]+; failed: 0; total: [0-9]+; seconds spent: [0-9]+.[0-9]+")

    def test_send_corrupted_file(self):
        pass

    def test_send_file_with_timestamps(self):
        pass

    def test_send_corrupted_file_with_timestamps(self):
        pass