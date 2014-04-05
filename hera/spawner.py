import select
import json
import time
import socket

from hera import vmcontroller_server
from hera import accounting
from hera import errors

MEMORY_RESERVE = 500 # mb
ESTIMATE_INTERVAL = 0.7
MIN_REQUEST_INTERVAL = 1

def loop(dispatcher_addr):
    sock = socket.socket()
    sock.connect(dispatcher_addr)
    f = sock.makefile('r+', 0)
    last_request_handled = 0
    while True:
        r, w, x = select.select([f], [], [f], ESTIMATE_INTERVAL)
        if x:
            raise errors.ConnectionError()
        response = {'estimates':
                    get_resources()}
        if r:
            delta = time.time() - last_request_handled
            sleep_time = MIN_REQUEST_INTERVAL - delta
            if sleep_time > 0:
                time.sleep(sleep_time)
            last_request_handled = time.time()
            request = f.readline()
            if not request:
                raise errors.ConnectionError()
            id, response = handle_request(json.loads(request))
            response['id'] = id
            response['response'] = response
        f.write(json.dumps(response) + '\n')
        f.flush()

def handle_request(request):
    resources = get_resources()
    for k, v in resources.items():
        if v < request[k]:
            response = None
            break
    else:
        response = vmcontroller_server.spawn(request)
    return request['id'], response

def get_mem_info():
    lines = [
        line.split()
        for line in open('/proc/meminfo') ]
    return { l[0][:-1]: int(l[1]) for l in lines }

def get_free_mem():
    info = get_mem_info()
    return (info['MemFree'] + info['Cached']) / 1024

def get_resources():
    return {
        'memory': get_free_mem() - MEMORY_RESERVE,
    }

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Connects to dispatcher and spawn VMs.')
    parser.add_argument('host', help='dispatcher host')
    parser.add_argument('port', type=int, help='dispatcher port', default=10001, nargs='?')
    args = parser.parse_args()
    addr = (args.host, args.port)
    loop(addr)
