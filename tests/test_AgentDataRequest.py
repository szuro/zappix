import unittest
from ast import literal_eval
from zappix.protocol import AgentData, AgentDataRequest


class TestAgentDataRequest(unittest.TestCase):
    def setUp(self):
        self.empty_agent = {"request": "agent data"}
        self.agent_with_data = {"request": "agent data", "data": [
                {"host": "testhost", "key": "testkey", "value": 1, "clock": 1554133179, "ns": 455816800, "id": 1},
                {"host": "testhost", "key": "testkey2", "value": 10, "clock": 1554133279, "ns": 555816800, "id": 2}
            ]}

    def test_basic_init(self):
        agent_request = AgentDataRequest()
        self.assertIsInstance(agent_request, AgentDataRequest)

        agent_request_dict = literal_eval(str(agent_request))
        self.assertIsNotNone(agent_request_dict.pop('session', None))

        self.assertDictEqual(
            agent_request_dict,
            self.empty_agent
            )

    def test_init_with_data(self):
        agent_request = AgentDataRequest(
            [AgentData('testhost', 'testkey', 1, 1554133179, 455816800),
             AgentData('testhost', 'testkey2', 10, 1554133279, 555816800)]
            )

        self.assertIsInstance(agent_request, AgentDataRequest)

        agent_request_dict = literal_eval(str(agent_request))
        self.assertIsNotNone(agent_request_dict.pop('session', None))

        self.assertDictEqual(
            agent_request_dict,
            self.agent_with_data
            )

    def test_init_with_invalid_data(self):
        with self.assertRaises(TypeError):
            AgentDataRequest([('testhost', 'testkey', 1)])

    def test_add_item(self):
        agent_request = AgentDataRequest()
        agent_request.add_item(AgentData('testhost', 'testkey', 1, 1554133179, 455816800))
        agent_request.add_item(AgentData('testhost', 'testkey2', 10, 1554133279, 555816800))

        agent_request_dict = literal_eval(str(agent_request))
        self.assertIsNotNone(agent_request_dict.pop('session', None))

        self.assertDictEqual(
            agent_request_dict,
            self.agent_with_data
            )

        self.assertListEqual([ar.id for ar in agent_request.data], [1, 2])

    def test_add_invalid_item(self):
        with self.assertRaises(TypeError):
            agent_request = AgentDataRequest()
            agent_request.add_item(('testhost', 'testkey', 1))
