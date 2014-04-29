from hera import accounting
from hera import errors

import socket
import queue
import collections
import threading
import uuid
import json
import logging
import bottle
import random

logger = logging.getLogger("dispatcher")

spawner_timeout = 5

dispatcher_queue = queue.Queue(0)
spawners = []

VmCreationRequest = collections.namedtuple('VmCreationRequest',
                                           'owner stats res_id')

def create_vm(owner, stats):
    res = accounting.add_derivative_vm_resource(owner, stats)
    try:
        return _create_vm(VmCreationRequest(owner, stats, res.id))
    except Exception:
        res.close()
        raise

def _create_vm(request):
    shuffled_spawners = list(spawners)
    random.shuffle(shuffled_spawners)
    for spawner in shuffled_spawners:
        result = spawner.create_vm_if_possible(request)
        if result:
            return result
    raise errors.ResourceNotAvailableError()

def spawners_loop():
    listen_sock = socket.socket()
    listen_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listen_sock.bind(('localhost', 10001))
    listen_sock.listen(5)
    while True:
        sock, addr = listen_sock.accept()
        Spawner(sock).start()

@bottle.post('/createvm')
def createvm():
    logger.info('Received createvm request')
    owner = bottle.request.forms['owner']
    stats = json.loads(bottle.request.forms['stats'])
    try:
        vm_id = create_vm(owner, stats)
    except errors.ResourceNotAvailableError:
        return {"status": "ResourceNotAvailableError"}
    else:
        return {"status": "ok", "id": vm_id}

def run_http_app():
    bottle.run(port=10002, server='cherrypy')

class Spawner:
    # Talks to spawner.py
    def __init__(self, socket):
        self.read_queues = {}
        self.write_lock = threading.Lock()
        self.estimate_lock = threading.Lock()
        self.estimates = None

        self.closed = False
        self.socket = socket
        self.socket.settimeout(spawner_timeout)
        self.file = self.socket.makefile('rw', 1)

    def start(self):
        logger.info("spawner connected")
        spawners.append(self)
        threading.Thread(target=self._socket_read_loop).start()

    def create_vm_if_possible(self, request):
        # If estimates show that it is possible,
        # asks spawner to create VM. Returns None
        # iff VM was not created.
        if self.closed:
            return None

        if not self.check_and_update_estimates(request):
            return None

        request_id = str(uuid.uuid4())
        q = queue.Queue(0)

        self.read_queues[request_id] = q
        try:
            self._write_spawn_request(request_id, request)
        except IOError:
            return None

        try:
            response = q.get(timeout=spawner_timeout)
        except queue.Empty:
            return None
        del self.read_queues[request_id]
        return response

    def check_and_update_estimates(self, request):
        # Check if spawner has enough resource that
        # it can handle `request`. If it has decrease
        # its resource estimates.
        if not self.estimates:
            return False

        with self.estimate_lock:
            new_estimates = {}
            for k, v in self.estimates.items():
                if request.stats[k] > v:
                    return False
                new_estimates[k] = v - request.stats[k]
            self.estimates = new_estimates
            return True

    def _write_spawn_request(self, id, request):
        with self.write_lock:
            data = dict(request.__dict__,
                        id=id)
            self.file.write("%s\n" %
                            json.dumps(data))
            self.file.flush()

    def _socket_read_loop(self):
        try:
            while True:
                self._socket_read_one()
        except errors.ConnectionError:
            pass
        finally:
            self.close()

    def _socket_read_one(self):
        data = self._socket_read_request()
        if 'id' in data:
            id = data['id']
            self.read_queues[id].put(data['response'])
        self.estimates = data['estimates']

    def _socket_read_request(self):
        data = self.file.readline()
        if not data:
            raise errors.ConnectionError()
        return json.loads(data)

    def close(self):
        self.closed = True
        self.socket.close()
        self._abort_all_requests()
        spawners.remove(self)
        logger.info('spawner disconnected')

    def _abort_all_requests(self):
        for q in list(self.read_queues.values()):
            q.put(None)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    threading.Thread(target=run_http_app).start()
    spawners_loop()
