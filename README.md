

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
