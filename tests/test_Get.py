import unittest
import configparser
import os
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

    def test_get_value_unsupported(self):
        resp = self.get.get_value("agent.pong")
        self.assertEqual(resp, 'ZBX_NOTSUPPORTED\x00Unsupported item key.')

    def test_get_report(self):
        resp = self.get.get_report(['agent.ping', 'agent.pong'])
        self.assertDictEqual(resp, {'agent.ping': '1', 'agent.pong': 'ZBX_NOTSUPPORTED\x00Unsupported item key.'})