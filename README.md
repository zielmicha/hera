### External dependencies

* python-3.4
* debootstrap
* supervisord
* eatmydata
* openvpn
* qemu-system-x86_64
* npm
* build-essential

You should install relatively new `pip`, `virtualenv` and `requests`. There seems to be a bug in `urllib3` shipped in e.g. Debian 8, which prevents `virtualenv` from creating envrionment.

```
pip3 install --upgrade pip virtualenv requests
```

### Interhost communication

(X connects to Y)

* spawner -> dispatcher (VM creation, port 10001, TLS+client auth)
* REST -> dispatcher (VM creation, port 10002, HTTP)
* REST -> vmcontroller (commands, random port, socket)
* agent -> stream proxy (HTTP)

### Pretty graph

```

          client-------
            |          \-----+
            |                |
        REST server     stream proxy
            |     \          |
            |      ---+      \
        dispatcher    |       |
            \         |       +---+
             \        |           |
          spawner     |           |
               +------+           |
                      |           |
                  vmcontroller    |
                      +-----------+
                                  |
                                agent

```
