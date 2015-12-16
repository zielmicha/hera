import select
import json
import time
import socket
import traceback
import logging
import os
import signal
import collections

from hera import vmcontroller_server
from hera import errors

ChildSpec = collections.namedtuple('ChildSpec', 'slots')

MEMORY_RESERVE = 500 # mb
ESTIMATE_INTERVAL = 0.7
MIN_REQUEST_INTERVAL = 1

logger = logging.getLogger("spawner")

class Spawner:
    def __init__(self):
        self.alive_children = {}
        self.slots = 1000

    def handle_sigchild(self, no, frame):
        while True:
            try:
                pid, exit_status = os.waitpid(-1, os.WNOHANG)
            except OSError:
                break

            try:
                child = self.alive_children[pid]
                del self.alive_children[pid]
            except KeyError:
                pass
            else:
                self.slots += child.slots


    def loop_retrying(self, addr):
        while True:
            try:
                self.loop(addr)
            except:
                traceback.print_exc()
                time.sleep(1)


    def loop(self, dispatcher_addr):
        sock = socket.socket()
        sock.connect(dispatcher_addr)

        signal.signal(signal.SIGCHLD, self.handle_sigchild)

        logging.info('connected to %r', dispatcher_addr)
        f = sock.makefile('rw', 1)
        last_request_handled = 0

        while True:
            try:
                r, w, x = select.select([sock], [], [sock], ESTIMATE_INTERVAL)
            except InterruptedError: continue
            if x:
                raise errors.ConnectionError()
            response = {'estimates':
                        self.get_resources()}
            if r:
                delta = time.time() - last_request_handled
                sleep_time = MIN_REQUEST_INTERVAL - delta
                if sleep_time > 0:
                    time.sleep(sleep_time)
                last_request_handled = time.time()
                request = f.readline()
                if not request:
                    raise errors.ConnectionError()
                request_id, vmid = self.handle_request(json.loads(request))
                response['id'] = request_id
                response['response'] = vmid

            f.write(json.dumps(response) + '\n')
            f.flush()

    def handle_request(self, request):
        resources = self.get_resources()
        stats = request['stats']
        for k, v in list(resources.items()):
            if v < stats[k]:
                response = None
                break
        else:
            response, pid = vmcontroller_server.spawn(request)
            self.alive_children[pid] = ChildSpec(slots=stats['slots'])
            self.slots -= stats['slots']

        return request['id'], response

    def get_resources(self):
        return {
            'memory': get_free_mem() - MEMORY_RESERVE,
            'slots': self.slots
        }


def get_mem_info():
    lines = [
        line.split()
        for line in open('/proc/meminfo') ]
    return { l[0][:-1]: int(l[1]) for l in lines }

def get_free_mem():
    info = get_mem_info()
    return (info['MemFree'] + info['Cached']) / 1024

if __name__ == '__main__':
    import django
    django.setup()

    logging.basicConfig(level=logging.INFO)
    import argparse
    parser = argparse.ArgumentParser(description='Connects to dispatcher and spawn VMs.')
    parser.add_argument('host', help='dispatcher host')
    parser.add_argument('port', type=int, help='dispatcher port', default=10001, nargs='?')
    args = parser.parse_args()
    addr = (args.host, args.port)

    Spawner().loop_retrying(addr)
