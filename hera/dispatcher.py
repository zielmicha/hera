from hera import accounting
from hera import errors

import socket
import Queue
import collections
import threading
import uuid
import json
import logging

logger = logging.getLogger("dispatcher")

spawner_timeout = 5

dispatcher_queue = Queue.Queue(0)
spawners = {}

VmCreationRequest = collections.namedtuple('VmCreationRequest',
                                           'owner stats res_id')

def create_vm(owner, stats):
    res = accounting.add_derivative_resource(owner, stats,
                                             timeout=60)
    try:
        _create_vm(VmCreationRequest(owner, stats, res.id))
    except Exception:
        res.close()
        raise

def _create_vm(request):
    for spawner in spawners:
        result = spawner.create_vm_if_possible(request)
        if result:
            return result
    raise errors.ResourceNotAvailableError()

def loop():
    listen_sock = socket.socket()
    listen_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listen_sock.bind(('localhost', 10001))
    listen_sock.listen(5)
    while True:
        sock, addr = listen_sock.accept()
        Spawner(sock).start()

class Spawner:
    # Talks to spawner.py
    def __init__(self, socket):
        self.read_queues = {}
        self.write_lock = threading.Lock()
        self.estimate_lock = threading.Lock()
        self.estimates = None

        self.socket = socket
        self.socket.settimeout(spawner_timeout)
        self.file = self.socket.makefile('r+', 1)

    def start(self):
        logger.info("spawner connected")
        threading.Thread(target=self._socket_read_loop).start()

    def create_vm_if_possible(self, request):
        # If estimates show that it is possible,
        # asks spawner to create VM. Returns None
        # iff VM was not created.
        if not self.check_and_update_estimates(request):
            return False

        request_id = str(uuid.uuid4())
        queue = Queue.Queue(0)

        self.read_queues[request_id] = queue
        self._write_spawn_request(request_id, request)

        response = queue.get()
        del self.response[request_id]
        return response

    def check_and_update_estimates(self, request):
        # Check if spawner has enough resource that
        # it can handle `request`. If it has decrease
        # its resource estimates.
        if not self.estimates:
            return False

        with self.estimate_lock:
            new_estimates = {}
            for k, v in self.estimates:
                if request.stats[k] > v:
                    return False
                new_estimates = v - request.stats[k]
            self.estimates = new_estimates
            return True

    def _write_spawn_request(self, id, request):
        with self.write_lock:
            data = dict(request.__dict__,
                        id=id)
            self.file.write("%s\n" %
                            json.dumps(data))

    def _socket_read_loop(self):
        try:
            while True:
                self._socket_read_one()
        finally:
            self.socket.close()
            self._abort_all_requests()

    def _socket_read_one(self):
        data = self._socket_read_request()
        if 'id' in data:
            id = data['id']
            self.response[id].put(data['response'])
        self.estimates = data['estimates']

    def _socket_read_request(self):
        data = self.file.readline()
        return json.loads(data)

    def _abort_all_requests(self):
        for q in self.read_queues.values():
            q.push(None)

if __name__ == '__main__':
    loop()
