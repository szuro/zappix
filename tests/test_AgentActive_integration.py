import unittest
import os
import time
import tempfile
import socket
import random
from zappix.agent_active import AgentActive
from zappix.protocol import ServerResponse, AgentDataRequest, AgentData
from pyzabbix import ZabbixAPI
from tests.utils import (zabbix_server_address,
                         zabbix_default_user,
                         zabbix_default_password,
                         create_host,
                         create_item,
                         remove_host)


class _BaseIntegrationTest(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.active = AgentActive('testhost', zabbix_server_address)
        self.zapi = ZabbixAPI('http://' + zabbix_server_address)
        self.zapi.login(zabbix_default_user, zabbix_default_password)
        self.hostid = create_host(self.zapi, 'testhost')
        create_item(self.zapi, self.hostid, 7)

        CacheUpdateFrequency = 5
        time.sleep(CacheUpdateFrequency)

    @classmethod
    def tearDownClass(self):
        remove_host(self.zapi, self.hostid)
        self.zapi.user.logout()


class TestAgentActive(_BaseIntegrationTest):
    def test_get_active_checks(self):
        checks = self.active.get_active_checks()
        self.assertIsNotNone(checks)
        self.assertEqual(len(checks), 1)

        self.assertEqual(checks[0].key, 'test')

    def test_send_agent_active_values(self):
        item_value = AgentData('testhost', 'test', 20, int(time.time()//1), 0)
        data = AgentDataRequest([item_value])
        response = self.active.send_collected_data(data)

        self.assertAlmostEqual(response.response, 'success')
        self.assertIsNotNone(response.info.pop('seconds spent'))
        self.assertDictEqual(response.info, {"processed": 1, "failed": 0, "total": 1})


if __name__ == '__main__':
    unittest.main()
