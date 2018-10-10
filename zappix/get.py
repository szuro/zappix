"""
Python implementation of Zabbix get.
"""

from zappix.dstream import _Dstream


class Get(_Dstream):
    """
    Class implementing zabbix_get utility.

    Parameters
    ----------
    :host:
        IP address of target host.
    :port:
        Port on which the Zabbix Agent listens.
    :source_address:
        Source IP address.
    """

    def __init__(self, host, port=10050, source_address=None):
        super().__init__(host, port, source_address)

    def get_value(self, key):
        """
        Get value of a single item identified by key.

        Parameters
        ----------
        :key:
            String representing an item key.

        Returns
        -------
        string
            Value of item.
        """
        payload = key + "\n"
        payload = payload.encode('utf-8')

        return self._send(payload)

    def get_report(self, keys):
        """
        Get value of a single item identified by key.

        Parameters
        ----------
        :keys:
            Iterable containing string representing item keys.

        Return
        ------
        dict
            Dict containing keys with corresponding values.
        """

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
        zab = Get(args.host, args.port, args.source_address)
    else:
        zab = Get(args.host, args.port)

    result = zab.get_value(args.key)
    print(result)
