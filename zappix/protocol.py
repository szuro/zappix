"""
Module containing models for Zabbix protocol.
"""

import abc


class _Model(abc.ABC):
    __slots__ = []

    def __init__(self):
        pass

    def __repr__(self):
        d = {k: getattr(self, k) for k in type(self).__slots__ if getattr(self, k, False)}
        return str(d)


class ItemData(_Model):
    __slots__ = ['host', 'key', 'value', 'clock']

    def __init__(self, host, key, value, clock=None):
        super().__init__()
        self.host = host
        self.key = key
        self.value = value
        self.clock = clock


SenderData = ItemData


class AgentData(ItemData):
    __slots__ = ItemData.__slots__ + ['ns', 'id', 'state']

    def __init__(self, host, key, value, clock, ns, state=None):
        super().__init__(host, key, value, clock)
        self.ns = ns
        self.id = 0
        self.state = state


class _TrapperRequest(_Model, abc.ABC):
    __slots__ = ['request', 'data', 'host', 'clock', 'ns', 'session']
    __supported_requests = ["active checks", "agent data", "sender data"]

    def __init__(self, request, **kwargs):
        super().__init__()
        if request not in _TrapperRequest.__supported_requests:
            raise ValueError
        self.request = request
        self.host = kwargs.get('host')
        self.data = kwargs.get('data')
        if self.data:
            self._check_items_classes(self.data, kwargs.get('item_class'))
        elif not self.data:
            self.data = []
        self.clock = kwargs.get('clock')
        self.ns = kwargs.get('ns')
        self.session = kwargs.get('session')

    def _check_items_classes(self, items, item_class):
        if not all(self._check_item_class(i, item_class) for i in items):
            raise ValueError

    def _check_item_class(self, item, item_class):
        return isinstance(item, item_class)


class ActiveChecksRequest(_TrapperRequest):
    def __init__(self, host):
        super().__init__(request="active checks", host=host)


class SenderDataRequest(_TrapperRequest):
    __item_class = SenderData

    def __init__(self, data=None):
        super().__init__(
            request="sender data",
            data=data,
            item_class=SenderDataRequest.__item_class
            )

    def add_item(self, item):
        if not self._check_item_class(item, SenderDataRequest.__item_class):
            raise ValueError
        self.data.append(item)


class AgentDataRequest(_TrapperRequest):
    __item_class = AgentData

    def __init__(self, data=None):
        super().__init__(
            request="agent data",
            data=data,
            item_class=AgentDataRequest.__item_class
            )

        self.item_id = 1
        for d in self.data:
            d.id = self.item_id
            self.item_id += 1

    def add_item(self, item):
        if not self._check_item_class(item, AgentDataRequest.__item_class):
            raise ValueError
        item.id = self.item_id
        self.data.append(item)
        self.item_id += 1
