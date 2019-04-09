zabbix_server_address = 'zabbix-server'
zabbix_default_user = 'Admin'
zabbix_default_password = 'zabbix'


def create_host(zapi, hostname):
    interface = {
                "type": 1,
                "main": 1,
                "useip": 1,
                "ip": "127.0.0.1",
                "dns": "",
                "port": "10050"
            }

    hosts = zapi.host.create(
        host=hostname,
        interfaces=[interface],
        groups=[{"groupid": 2}]
        )

    return hosts['hostids'][0]


def create_item(zapi, hostid, item_type=2):
    zapi.item.create(
        hostid=hostid,
        key_='test',
        name='test',
        type=item_type,
        value_type=3
    )


def remove_host(zapi, hostid):
    zapi.host.delete(hostid)
