import unittest
from zappix.get import Get


zabbix_agent_address = 'zabbix-agent'


class TestGetValue(unittest.TestCase):
    def setUp(self):
        self.get = Get(zabbix_agent_address)

    def test_get_value(self):
        resp = self.get.get_value("agent.ping")
        self.assertEqual(resp, '1')

    def test_get_value_unsupported(self):
        resp = self.get.get_value("agent.pong")
        self.assertEqual(resp, 'ZBX_NOTSUPPORTED\x00Unsupported item key.')

    def test_get_report(self):
        resp = self.get.get_report(['agent.ping', 'agent.pong'])
        self.assertDictEqual(resp, {'agent.ping': '1', 'agent.pong': 'ZBX_NOTSUPPORTED\x00Unsupported item key.'})


class TestGetValueWithBoundAddress(TestGetValue):
    def setUp(self):
        self.get = Get(zabbix_agent_address, source_address='localhost')


if __name__ == '__main__':
    unittest.main()
