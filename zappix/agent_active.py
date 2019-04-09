from zappix.protocol import ActiveChecksRequest, AgentDataRequest, ModelEncoder
from zappix.protocol import ServerResponse
from zappix.dstream import _Dstream
import json


class AgentActive(_Dstream):
    def __init__(self, host, server, server_port=10051, source_address=None):
        super().__init__(server, server_port, source_address)
        self._host = host

    def get_active_checks(self):
        request = ActiveChecksRequest(self._host)
        result = self._send(
            json.dumps(request, cls=ModelEncoder).encode("utf-8")
            )
        return ServerResponse(result).data

    def send_collected_data(self, data):
        if not isinstance(data, AgentDataRequest):
            raise ValueError
        result = self._send(
            json.dumps(data, cls=ModelEncoder).encode("utf-8")
            )
        return ServerResponse(result)
