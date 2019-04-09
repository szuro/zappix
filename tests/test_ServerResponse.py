import unittest
from zappix.protocol import ServerResponse


class TestServerResponse(unittest.TestCase):
    def setUp(self):
        self.response_active_items = (
            '{"response":"success",'
            '"data":['
            '{"key":"log[/home/zabbix/logs/zabbix_agentd.log]",'
            '"delay":30,'
            '"lastlogsize":0,'
            '"mtime":0},'
            '{"key":"agent.version",'
            '"delay":600,'
            '"lastlogsize":0,'
            '"mtime":0}]}')

        self.response_items_send = ('{"response":"success",'
                                    '"info":"processed: 3;'
                                    'failed: 0; total: 3;'
                                    'seconds spent: 0.003534"}')

    def test_response_after_sending_collected_data(self):
        response = ServerResponse(self.response_items_send)
        self.assertEqual(response.response, 'success')
        self.assertDictEqual(response.info, {'processed': 3,
                                             'failed': 0,
                                             'total': 3,
                                             'seconds spent': 0.003534})
        self.assertListEqual(response.data, [])

    def test_response_with_active_checks(self):
        response = ServerResponse(self.response_active_items)
        self.assertEqual(response.response, 'success')
        self.assertEqual(len(response.data), 2)

        # Note: order of items is reversed due to while/pop
        self.assertEqual(response.data[1].key,
                         "log[/home/zabbix/logs/zabbix_agentd.log]")
        self.assertEqual(response.data[1].delay, 30)
        self.assertEqual(response.data[1].lastlogsize, 0)
        self.assertEqual(response.data[1].mtime, 0)
