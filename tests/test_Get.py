import unittest
import configparser
import os
import tempfile
from zappix.get import Get


class GetValueTest(unittest.TestCase):
    def setUp(self):
        config = configparser.ConfigParser()
        this_path = os.path.dirname(os.path.abspath(__file__))
        config.read(os.path.join(this_path, 'test.ini'))
        self.agent = config['agent']['good']

        self.get = Get(self.agent)

    def test_get_value(self):
        resp = self.get.get_value("agent.ping")
        self.assertEqual(resp, '1')