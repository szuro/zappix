import unittest
import configparser
import os
import time
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
        self.assertRegex(resp, r"processed: 1; failed: 0; total: 1; seconds spent: [0-9]+.[0-9]+")

    def test_bad_value(self):
        resp = self.sender.send_value('testhost','test', "bad_value")
        self.assertIsNotNone(resp)
        self.assertRegex(resp, r"processed: 0; failed: 1; total: 1; seconds spent: [0-9]+.[0-9]+")

    def test_bad_key(self):
        resp = self.sender.send_value('testhost','bad_key', 1)
        self.assertIsNotNone(resp)
        self.assertRegex(resp, r"processed: 0; failed: 1; total: 1; seconds spent: [0-9]+.[0-9]+")

    def test_bad_hostname(self):
        resp = self.sender.send_value('bad_host','test', 1)
        self.assertIsNotNone(resp)
        self.assertRegex(resp, r"processed: 0; failed: 1; total: 1; seconds spent: [0-9]+.[0-9]+")

    @unittest.skip
    def test_bad_server(self):
        sender = Sender('127.0.0.2')
        resp = sender.send_value('testhost','test', 1)
        self.assertIsNotNone(resp)

    @unittest.skip
    def test_bad_port(self):
        sender = Sender(self.server, 666)
        resp = sender.send_value('testhost','test', 1)
        self.assertIsNotNone(resp)


class SenderFileTest(unittest.TestCase):
    def setUp(self):
        config = configparser.ConfigParser()
        this_path = os.path.dirname(os.path.abspath(__file__))
        config.read(os.path.join(this_path, 'test.ini'))
        self.server = config['server']['good']

        self.sender = Sender(self.server)
        
        self.file = tempfile.NamedTemporaryFile('w+', delete=False)
        self.file.write("testhost test 1\n"
                        "testhost test 2\n"
                        "testhost test 3\n")
        self.file.close()

        self.file_with_timestamps = tempfile.NamedTemporaryFile('w+', delete=False)
        self.file_with_timestamps.write("testhost test {t} 10\n"
                                        "testhost test {t} 20\n"
                                        "testhost test {t} 30\n".format(t=int(time.time()//1)))
        self.file_with_timestamps.close()


    def tearDown(self):
        os.unlink(self.file.name)
        os.unlink(self.file_with_timestamps.name)

    def test_send_file(self):
        resp = self.sender.send_file(self.file.name)
        self.assertIsNotNone(resp)
        self.assertRegex(resp, r"processed: 3; failed: 0; total: 3; seconds spent: [0-9]+.[0-9]+")

    def test_send_corrupted_file(self):
        pass

    def test_send_file_with_timestamps(self):
        resp = self.sender.send_file(self.file_with_timestamps.name, with_timestamps=True)
        self.assertIsNotNone(resp)
        self.assertRegex(resp, r"processed: 3; failed: 0; total: 3; seconds spent: [0-9]+.[0-9]+")

    def test_send_corrupted_file_with_timestamps(self):
        pass