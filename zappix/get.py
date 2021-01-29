"""
Python implementation of Zabbix get.
"""

from typing import List, Dict, Optional
from zappix.dstream import _Dstream
import logging

logger = logging.getLogger(__name__)


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

    def __init__(self, host: str, port: int = 10050, source_address: Optional[str] = None) -> None:
        super().__init__(host, port, source_address)

    def _pack_key(self, key: str) -> bytes:
        _key = f"{key}\n".encode('utf-8')
        logging.info(f"Getting {key} from {self._ip}:{self._port}")
        return _key

    def get_value(self, key: str) -> str:
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

        return self._send(
            self._pack_key(key)
            )

    def get_report(self, keys: List[str]) -> Dict[str, str]:
        """
        Get value of a item identified by keys provided in supplied iterable.
        Note that there are executed synchronously, so the performance might not be ideal.

        Parameters
        ----------
        :keys:
            Iterable containing string representing item keys.

        Return
        ------
        dict
            Dict containing keys with corresponding values.
        """

        report = {key: self._send(self._pack_key(key)) for key in keys}
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
