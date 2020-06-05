"""
Module containing models for Zabbix protocol.
"""

from typing import List, Any, Optional, Dict, Union
import abc
import json
from ast import literal_eval
from uuid import uuid4


class _Model(abc.ABC):
    __slots__: List[str] = []

    def __init__(self) -> None:
        pass

    def __repr__(self) -> str:
        return str(ModelEncoder().default(self))


class ModelEncoder(json.JSONEncoder):
    """
    Class for encoding to JSON models implemented herein.
    """
    def default(self, o: _Model) -> Dict[str, Any]:
        d = {k: getattr(o, k) for k in type(o).__slots__ if getattr(o, k, False)}
        return d


class ItemData(_Model):
    """
    Class model representing data to be sent to a trapper item.

    Parameters
    ----------
    :host:
        Hostname to which the item belongs.
    :key:
        Item key
    :value:
        Value to be sent.
    :clock:
        Timestamp at which value was collected.
    """
    __slots__ = ['host', 'key', 'value', 'clock']

    def __init__(self, host: str, key: str, value: Any, clock: Optional[int] = None) -> None:
        super().__init__()
        self.host = host
        self.key = key
        self.value = value
        self.clock = clock


SenderData = ItemData


class AgentData(ItemData):
    """
    Class model representing data to be sent to a Zabbix agent (active) item.

    Parameters
    ----------
    :host:
        Hostname to which the item belongs.
    :key:
        Item key
    :value:
        Value to be sent.
    :clock:
        Timestamp at which value was collected.
    :ns:
        Nanoseconds for clock
    :state:
        State of an item. Set to 1 for Unsupported.

    Attributes
    ----------
    :id:
        Unique id for item within one session.
    """
    __slots__ = ItemData.__slots__ + ['ns', 'id', 'state']

    def __init__(self, host: str, key: str, value: Any, clock: int, ns: int, state: Optional[int] = None) -> None:
        super().__init__(host, key, value, clock)
        self.ns = ns
        self.id = 0
        self.state = state


class _TrapperRequest(_Model, abc.ABC):
    __slots__ = ['request', 'data', 'host', 'clock', 'ns', 'session']
    __supported_requests = ["active checks", "agent data", "sender data"]

    def __init__(self, request: str, **kwargs) -> None:
        super().__init__()
        if request not in _TrapperRequest.__supported_requests:
            raise ValueError
        self.request = request
        self.host = kwargs.get('host')
        self.data = kwargs.get('data', [])
        if self.data:
            self._check_items_classes(self.data, kwargs.get('item_class'))
        elif not self.data:
            self.data = []
        self.clock = kwargs.get('clock')
        self.ns = kwargs.get('ns')
        self.session = kwargs.get('session')

    def _check_items_classes(self, items, item_class):
        if not all(self._check_item_class(i, item_class) for i in items):
            raise TypeError

    def _check_item_class(self, item, item_class):
        return isinstance(item, item_class)


class ActiveChecksRequest(_TrapperRequest):
    """
    Class implementing protocol for requesting active checks for host.

    Parameters
    ----------
    :host:
        Get active checks for specified host.
    """
    def __init__(self, host: str) -> None:
        super().__init__(request="active checks", host=host)


class SenderDataRequest(_TrapperRequest):
    """
    Class implementing protocol for sending data with sender protocol.

    Parameters
    ----------
    :data:
        List of SenderData objects.
    """
    __item_class = SenderData

    def __init__(self, data: Optional[List[SenderData]] = None) -> None:
        super().__init__(
            request="sender data",
            data=data,
            item_class=SenderDataRequest.__item_class
            )

    def add_item(self, item: SenderData) -> None:
        """
        Add data to request.

        Parameters
        ----------
        :item:
            Instance of SenderData.
        """
        if not self._check_item_class(item, SenderDataRequest.__item_class):
            raise TypeError
        self.data.append(item)


class AgentDataRequest(_TrapperRequest):
    """
    Class implementing protocol for sending data gathered by active checks.
    Each instance should be used as unique data session.

    Parameters
    ----------
    :data:
        List of AgentData objects.
    """
    __item_class = AgentData

    def __init__(self, data: Optional[List[AgentData]] = None) -> None:
        super().__init__(
            request="agent data",
            data=data,
            item_class=AgentDataRequest.__item_class,
            session=uuid4().hex
            )

        self._item_id = 1
        if self.data:
            for d in self.data:
                d.id = self._item_id
                self._item_id += 1

    def add_item(self, item: AgentData) -> None:
        """
        Add data to request and assign an id to it.

        Parameters
        ----------
        :item:
            Instance of AgentData.
        """
        if not self._check_item_class(item, AgentDataRequest.__item_class):
            raise TypeError
        item.id = self._item_id
        self.data.append(item)
        self._item_id += 1


class ActiveItem:
    """
    Zabbix active item configuration.
    """

    __slots__ = ['key', 'delay', 'lastlogsize', 'mtime']

    def __init__(self, key: str, delay: int, lastlogsize: int = 0, mtime: int = 0) -> None:
        self.key = key
        self.delay = delay
        self.lastlogsize = lastlogsize
        self.mtime = mtime


class ServerResponse:
    """
    Class representing server responses.
    """
    def __init__(self, response: str) -> None:
        self.response = None
        self.data: List[ActiveItem] = []
        self._info: Dict[str, Any] = {}
        self._parse_response(response)

    @property
    def info(self) -> Union[Dict[str, Any], None]:
        return self._info if self._info else None

    def _parse_data(self, data):
        while data:
            item = data.pop()
            self.data.append(
                ActiveItem(item['key'],
                           item['delay'],
                           item['lastlogsize'],
                           item['mtime'])
            )

    def _parse_info(self, info):
        if not info:
            return None
        parts = (part.split(':') for part in info.split(';'))
        self._info = {k.strip(): literal_eval(v.strip()) for k, v in parts}

    def _parse_response(self, response):
        if response:
            loaded = json.loads(response)
            self.response = loaded['response']
            self._parse_info(loaded.get('info', None))
            self._parse_data(loaded.get('data', []))
