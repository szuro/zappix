import unittest
import os
import time
import tempfile
import socket
import random
from zappix.sender import Sender
from zappix.protocol import SenderDataRequest, SenderData
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
        self.sender = Sender(zabbix_server_address)
        self.zapi = ZabbixAPI('http://' + zabbix_server_address)
        self.zapi.login(zabbix_default_user, zabbix_default_password)
        self.hostid = create_host(self.zapi, 'testhost')
        create_item(self.zapi, self.hostid)

        CacheUpdateFrequency = 5
        time.sleep(CacheUpdateFrequency)

    @classmethod
    def tearDownClass(self):
        remove_host(self.zapi, self.hostid)
        self.zapi.user.logout()


class TestSenderValue(_BaseIntegrationTest):
    def test_send_single_value(self):
        resp = self.sender.send_value('testhost', 'test', 1)
        self.assertIsNotNone(resp.pop("seconds spent"))
        self.assertDictEqual(resp, {"processed": 1, "failed": 0, "total": 1})

    @unittest.skip("Behaviour inconsistent across Zabbix versions")
    def test_send_bad_value(self):
        resp = self.sender.send_value('testhost', 'test', "bad_value")
        self.assertIsNotNone(resp.pop("seconds spent"))
        self.assertDictEqual(resp, {"processed": 0, "failed": 1, "total": 1})

    def test_send_bad_key(self):
        resp = self.sender.send_value('testhost', 'bad_key', 1)
        self.assertIsNotNone(resp.pop("seconds spent"))
        self.assertDictEqual(resp, {"processed": 0, "failed": 1, "total": 1})

    def test_send_bad_hostname(self):
        resp = self.sender.send_value('bad_host', 'test', 1)
        self.assertIsNotNone(resp.pop("seconds spent"))
        self.assertDictEqual(resp, {"processed": 0, "failed": 1, "total": 1})

    def test_send_bad_server(self):
        sender = Sender('nonexisting-server')
        resp = sender.send_value('testhost', 'test', 1)
        self.assertIsNone(resp)

    def test_send_bad_port(self):
        sender = Sender(zabbix_server_address, 666)
        resp = sender.send_value('testhost', 'test', 1)
        self.assertIsNone(resp)


class TestSenderFile(_BaseIntegrationTest):
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
        file_ = tempfile.NamedTemporaryFile('w+', delete=False)
        file_.write("testhost test {t} 10\n"
                    "testhost test  {t}  20\n"
                    "testhost   test {t} 30\n".format(t=int(time.time()//1)))
        file_.close()
        resp, _ = self.sender.send_file(file_.name, with_timestamps=True)
        os.unlink(file_.name)
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


class TestSenderBulk(_BaseIntegrationTest):
    def test_send_bulk(self):
        rq = SenderDataRequest(
            [
                SenderData('testhost', 'test', 1),
                SenderData('testhost', 'test', 20),
            ]
        )

        rq.add_item(SenderData('testhost', 'test', 300))

        resp = self.sender.send_bulk(rq)
        self.assertIsNotNone(resp.pop("seconds spent"))
        self.assertDictEqual(resp, {"processed": 3, "failed": 0, "total": 3})



@unittest.skipIf(True if os.environ.get('GITLAB_CI', '') else False, "Skipping on GitLab")
class TestSenderValueWithBoundAddress(TestSenderValue):
    def setUp(self):
        self.sender = Sender(zabbix_server_address, source_address=socket.gethostname())


class TestSenderDecorator(_BaseIntegrationTest):
    def test_send_single_value(self):
        @self.sender.send_result('testhost', 'test')
        def echo(number):
            return number

        number = random.randint(1, 100)
        res = echo(number)
        self.assertEqual(res, number)


if __name__ == '__main__':
    unittest.main()
