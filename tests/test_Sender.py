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
        resp = self.sender.send_value('testhost', 'test', 1)
        self.assertIsNotNone(resp.pop("seconds spent"))
        self.assertDictEqual(resp, {"processed": 1, "failed": 0, "total": 1})

    def test_bad_value(self):
        resp = self.sender.send_value('testhost', 'test', "bad_value")
        self.assertIsNotNone(resp.pop("seconds spent"))
        self.assertDictEqual(resp, {"processed": 0, "failed": 1, "total": 1})

    def test_bad_key(self):
        resp = self.sender.send_value('testhost', 'bad_key', 1)
        self.assertIsNotNone(resp.pop("seconds spent"))
        self.assertDictEqual(resp, {"processed": 0, "failed": 1, "total": 1})

    def test_bad_hostname(self):
        resp = self.sender.send_value('bad_host', 'test', 1)
        self.assertIsNotNone(resp.pop("seconds spent"))
        self.assertDictEqual(resp, {"processed": 0, "failed": 1, "total": 1})

    def test_bad_server(self):
        sender = Sender('127.0.0.2')
        resp = sender.send_value('testhost', 'test', 1)
        self.assertIsNone(resp)

    def test_bad_port(self):
        sender = Sender(self.server, 666)
        resp = sender.send_value('testhost', 'test', 1)
        self.assertIsNone(resp)


class SenderFileTest(unittest.TestCase):
    def setUp(self):
        config = configparser.ConfigParser()
        this_path = os.path.dirname(os.path.abspath(__file__))
        config.read(os.path.join(this_path, 'test.ini'))
        self.server = config['server']['good']

        self.sender = Sender(self.server)

    def test_send_file(self):
        file_ = tempfile.NamedTemporaryFile('w+', delete=False)
        file_.write("testhost test 1\n"
                    "testhost test  2\n"
                    "testhost test   3\n")
        file_.close()
        resp, _ = self.sender.send_file(file_.name)
        os.unlink(file_.name)
        self.assertIsNotNone(resp.pop("seconds spent"))
        self.assertDictEqual(resp, {"processed": 3, "failed": 0, "total": 3})

    def test_send_corrupted_file(self):
        file_ = tempfile.NamedTemporaryFile('w+', delete=False)
        file_.write("testhost test 1\n"
                    "testhost test\n"
                    "testhost test \n"
                    "testhost test 3\n")
        file_.close()
        resp, corrupted_lines = self.sender.send_file(file_.name)
        os.unlink(file_.name)
        self.assertSequenceEqual(corrupted_lines, [2, 3])
        self.assertIsNotNone(resp.pop("seconds spent"))
        self.assertDictEqual(resp, {"processed": 2, "failed": 0, "total": 2})

    def test_send_file_with_timestamps(self):
        file_with_timestamps = tempfile.NamedTemporaryFile('w+', delete=False)
        file_with_timestamps.write("testhost test {t} 10\n"
                                   "testhost test  {t}  20\n"
                                   "testhost   test {t} 30\n".format(t=int(time.time()//1)))
        file_with_timestamps.close()
        resp, _ = self.sender.send_file(file_with_timestamps.name, with_timestamps=True)
        os.unlink(file_with_timestamps.name)
        self.assertIsNotNone(resp.pop("seconds spent"))
        self.assertDictEqual(resp, {"processed": 3, "failed": 0, "total": 3})

    def test_send_corrupted_file_with_timestamps(self):
        file_ = tempfile.NamedTemporaryFile('w+', delete=False)
        file_.write("testhost test {t} 10\n"
                    "testhost test\n"
                    "testhost   test {t} \n"
                    "testhost test {t} 2\n".format(t=int(time.time()//1)))
        file_.close()
        resp, corrupted_lines = self.sender.send_file(file_.name, with_timestamps=True)
        os.unlink(file_.name)
        self.assertSequenceEqual(corrupted_lines, [2, 3])
        self.assertIsNotNone(resp.pop("seconds spent"))
        self.assertDictEqual(resp, {"processed": 2, "failed": 0, "total": 2})


class SenderValueWithBoundAddressTest(unittest.TestCase):
    def setUp(self):
        config = configparser.ConfigParser()
        this_path = os.path.dirname(os.path.abspath(__file__))
        config.read(os.path.join(this_path, 'test.ini'))
        self.server = config['server']['good']

        self.sender = Sender(self.server, source_address=config['agent']['good'])
