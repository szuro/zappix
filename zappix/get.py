from __future__ import print_function, unicode_literals, absolute_import, division
from zappix.dstream import Dstream
import json


class Get(Dstream):

    def __init__(self, host, port=10050, source_address=None):
        super().__init__(host, port, source_address)

    def get_value(self, key):
        payload = key + "\n"
        payload = payload.encode('utf-8')

        return self._send(payload)

    def get_report(self, keys):
        report = {key: self._send((key + '\n').encode('utf-8')) for key in keys}
        return report


if __name__ == '__main__':
    import argparse
    params = argparse.ArgumentParser()
    params.add_argument('-s', '--host', nargs='?')
    params.add_argument('-p', '--port', nargs='?', default=10050, type=int)
    params.add_argument('-I', '--source-address', nargs='?')
    params.add_argument('-k', '--key', nargs='?')
    args = params.parse_args()

    if args.source_address:
        zab = Get(args.zabbix, args.port, args.source_address)
    else:
        zab = Get(args.zabbix, args.port)

    result = zab.get_value(args.key)
    print(result['info'])
