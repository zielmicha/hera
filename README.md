

### Interhost communication

(X connects to Y)

* spawner -> dispatcher (port 10001, TLS+client auth)
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
             \/-------+           |
          spawner                 |
               +------+           |
                      |           |
                  vmcontroller    |
                      +-----------+
                                  |
                                agent

```
