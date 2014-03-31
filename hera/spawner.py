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
            sleep_time = time.time() - last_request_handled
            if sleep_time > 0:
                time.sleep(sleep_time)
            last_request_handled = time.time()
            request = f.readline()
            id, response = handle_request(request)
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
    return get_mem_info()['MemFree'] / 1024

def get_resources():
    return {
        'memory': get_free_mem() - MEMORY_RESERVE,
    }

if __name__ == '__main__':
    print get_free_mem()
