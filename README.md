![](logo/icon.png)

# sandbox as a service

* [API docs](https://users.atomshare.net/~zlmch/hera/build/)
* [Python API wrapper examples](https://github.com/zielmicha/hera/tree/master/examples)

More documentation on its way.

## License

* Hera server is GNU/AGPL-licensed
* Hera client libraries (heraclient.py) are MIT-licensed
* Hera examples/ are in public domain (CC0)

## Running Hera on your own cluster

### External dependencies

* python-3.4
* debootstrap
* supervisor
* eatmydata
* openvpn
* qemu-system-x86_64
* npm
* build-essential
* git

You should install relatively new `pip`, `virtualenv` and `requests`. There seems to be a bug in `urllib3` shipped in e.g. Debian 8, which prevents `virtualenv` from creating envrionment.

```
pip3 install --upgrade pip virtualenv requests
```

### Development dependencies

* bundler

### Interhost communication

(X connects to Y)

* spawner -> dispatcher (VM creation, port 10001)
* REST -> dispatcher (VM creation, port 10002, HTTP)
* REST -> vmcontroller (commands, random port, socket)
* agent -> stream proxy (HTTP)

All modules also require shared directory (e.g. mounted via NFS) `IMAGE_STORE` and a database connection.

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
