"""
Python implementation of Zabbix sender.
"""

from zappix.dstream import Dstream
import json
import csv
import time


class Sender(Dstream):
    """
    Class implementing zabbix_sender utility.

    Parameters
    ----------
    :server:
        IP address of target Zabbix Server.
    :port:
        Port on which the Zabbix Server listens.
    :source_address:
        Source IP address.
    """

    def __init__(self, server, port=10051, source_address=None):
        super().__init__(server, port, source_address)

    def send_value(self, host, key, value):
        """
        Send a single value to a Zabbix host.

        Parameters
        ----------
        :host:
            Name of a host as visible in Zabbix frontend.
        :key:
            String representing an item key.
        :value:
            Value to be sent.

        Returns
        -------
        string
            Information from server.
        """
        payload = {
            "request": "sender data",
            "data": []
            }

        payload["data"].append(
            self._create_payload(host, key, value)
            )

        response = self._send(json.dumps(payload).encode("utf-8"))
        return self._parse_server_info(response)

    def send_file(self, file, with_timestamps=False):
        """
        Send values contained in a file to specified hosts.

        Parameters
        ----------
        :file:
            Path to file with data.
        :with_timestamps:
            Specify whether file contains timestamps for items.

        Returns
        -------
        string
            Information from server.
        """
        response = self._send(self._parse_file(file, with_timestamps))
        return self._parse_server_info(response)

    def _parse_file(self, file, with_timestamps=False):
        with open(file, 'r', encoding='utf-8') as values:
            payload = {"request": "sender data", "data": []}
            reader = csv.reader(values, delimiter=' ')

            for row in reader:
                if with_timestamps:
                    payload["data"].append(self._create_payload(row[0], row[1], row[3], row[2]))
                else:
                    payload["data"].append(self._create_payload(row[0], row[1], row[2]))

        if with_timestamps:
            now = time.time()
            payload["clock"] = int(now//1)
            payload["ns"] = int(now % 1 * 1e9)

        return json.dumps(payload).encode("utf-8")

    def _create_payload(self, host, key, value, timestamp=None):
        payload = {
            "host": host,
            "key": key,
            "value": str(value)
        }
        if timestamp:
            payload["clock"] = timestamp
        return payload

    def _parse_server_info(self, resp):
        if resp:
            loaded = json.loads(resp)
            parts = (part.split(': ') for part in loaded["info"].split('; '))
            parsed = {k: eval(v) for k, v in parts}
            return parsed


if __name__ == '__main__':
    import argparse
    params = argparse.ArgumentParser()
    params.add_argument('-z', '--zabbix', nargs='?')
    params.add_argument('-p', '--port', nargs='?', default=10051, type=int)
    params.add_argument('-I', '--source-address', nargs='?')
    params.add_argument('-s', '--host', nargs='?')
    params.add_argument('-k', '--key', nargs='?')
    params.add_argument('-o', '--value', nargs='?')
    params.add_argument('-i', '--input-file', nargs='?')
    params.add_argument('-T', '--with-timestamps', action='store_true')
    args = params.parse_args()

    if args.source_address:
        zab = Sender(args.zabbix, args.port, args.source_address)
    else:
        zab = Sender(args.zabbix, args.port)

    if all([args.host, args.key, args.value]):
        result = zab.send_value(args.host, args.key, args.value)
    elif args.input_file:
        result = zab.send_file(args.input_file, True if args.with_timestamps else False)

    print('info from server: "{}"'.format(result))
