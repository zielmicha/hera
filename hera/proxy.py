import asyncio
import logging
import collections
import websockets

from hera import settings

buffer_size = 512
connections = collections.defaultdict(lambda: asyncio.Queue(buffer_size))
EOF = (object(), 'EOF') # marker

@asyncio.coroutine
def client_connected(reader, writer):
    hello = yield from reader.readline()
    attrs = decode_hello(hello)
    if not attrs:
        writer.write_eof()
        return

    client = yield from client_get(attrs)

    if not client:
        writer.write_eof()
        return

    asyncio.async(client_read(client, reader))
    asyncio.async(client_write(client, writer))


@asyncio.coroutine
def ws_client_connected(websocket, uri):
    prefix = '/stream/'
    if uri.startswith(prefix):
        attrs = decode_ws_uri(uri[len(prefix):])
        client = yield from client_get(attrs)

        if not client:
            return

        asyncio.async(ws_client_read(client, websocket))
        yield from ws_client_write(client, websocket)

def decode_ws_uri(uri):
    id, _, query = uri.partition('?')
    args = {'id': id}
    for part in query.split('&'):
        if '=' in part:
            k, v = part.split('=', 1)
            args[k] = v
    return args

@asyncio.coroutine
def client_get(attrs):
    id = attrs['id']
    role = attrs.get('role', 'client')
    if role not in ('client', 'server'):
        logging.warn('invalid role %r' % role)
        return None

    a, b = id + '_a', id + '_b'
    if role == 'server':
        a, b = b, a

    return a, b

@asyncio.coroutine
def client_read(client, reader):
    wrchan, rdchan = client
    while True:
        try:
            data = yield from reader.read(4096)
        except ConnectionError:
            break
        if not data:
            break
        yield from connections[rdchan].put(data)

    yield from connections[rdchan].put(EOF)

@asyncio.coroutine
def ws_client_read(client, websocket):
    wrchan, rdchan = client
    while True:
        data = yield from websocket.recv()
        yield from connections[rdchan].put(data)

    yield from connections[rdchan].put(EOF)

@asyncio.coroutine
def client_write(client, writer):
    wrchan, rdchan = client

    try:
        while True:
            data = yield from connections[wrchan].get()
            if data is EOF:
                writer.close()
                yield from writer.drain()
                break

            writer.write(data)

            yield from writer.drain()
    except ConnectionError:
        pass

@asyncio.coroutine
def ws_client_write(client, websocket):
    wrchan, rdchan = client

    while True:
        data = yield from connections[wrchan].get()
        if data is EOF:
            break

        yield from websocket.send(data)

def decode_hello(hello):
    parts = hello.decode('utf8').split()
    if not all( '=' in part for part in parts ):
        return None
    attrs = dict( part.split('=') for part in parts )
    if 'id' not in attrs:
        return None
    return attrs

@asyncio.coroutine
def main():
    host, port = settings.PROXY_RAW_ADDR
    yield from asyncio.start_server(client_connected,
                                    host=host, port=port)
    host, port = settings.PROXY_WS_ADDR
    yield from websockets.serve(ws_client_connected, host, port)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.run_forever()
    loop.close()
