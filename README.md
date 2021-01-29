# zappix - a package for Zabbix sender and get.

zappix aims to be a drop-in replacement for zabbix_get as well as zabbix_sender.
Its components are available not only as a module but from the command line as well.

zappix requires Python3 and is guaranteed to work with 3.6.

## Instalation 

zappix is not dependant on any third party modules.
The easiest way to install it with pip:
```sh
pip install zappix
```

# Usage

As mentioned earlier - zappix can be used both as a module inside of an application, as well as from the Command Line Interface.

## As a module

At the moment zappix has two classes: Sender and Get. Both of which can be imported in the following manner:
```python
>>> from zappix.sender import Sender
>>> from zappix.get import Get
```

Then you can send or get some data. Asuming both Zabbix Agent and Server run on localhost and default ports:

```python
>>> getter = Get("127.0.0.1")
>>> getter.get_value("agent.ping")
1
>>> sender = Sender("127.0.0.1")
>>> sender.send_value('testhost', 'test', 1)
{"processed": 1, "failed": 0, "total": 1, "seconds spent": 0.005}

```

## CLI

To use this utility from the command line, you need to invoke python with the -m flag, followed by the module name and required parameters:

```sh
python -m zappix.sender -z 127.0.0.1 -s testhost -k testkey -o 1
```
