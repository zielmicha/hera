from hera import accounting
from hera import errors
from hera import util
from hera.queue import VmCreationRequest, CreateQueue, create_vm_object

from cherrypy import wsgiserver
from flask import jsonify, request

import flask
import socket
import queue
import collections
import threading
import uuid
import json
import logging
import random

logger = logging.getLogger("dispatcher")

spawner_timeout = 5

dispatcher_queue = queue.Queue(0)
spawners = []

create_queue = CreateQueue()

http_app = flask.Flask(__name__)
http_app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

def create_vm(owner, stats, async, async_params=None):
    res = accounting.add_derivative_vm_resource(owner, stats)
    request = VmCreationRequest(owner, stats, res.id)
    if async:
        logger.info('Queuing sandbox creation')
        create_queue.queue(request, async_params)
        return request.res_id
    else:
        logger.info('Creating sandbox directly')
        try:
            return _create_vm(request)
        except Exception:
            res.close()
            raise

def _create_vm(request):
    shuffled_spawners = list(spawners)
    random.shuffle(shuffled_spawners)
    for spawner in shuffled_spawners:
        response = spawner.create_vm_if_possible(request)
        if response:
            return create_vm_object(request, response)
    raise errors.ResourceNotAvailableError()

def spawners_loop():
    listen_sock = socket.socket()
    listen_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listen_sock.bind(('localhost', 10001))
    listen_sock.listen(5)
    while True:
        sock, addr = listen_sock.accept()
        Spawner(sock).start()

@http_app.route('/createvm', methods=['POST'])
def createvm():
    logger.info('Received createvm request')
    owner = request.form['owner']
    stats = json.loads(request.form['stats'])
    async = util.is_true(request.form['async'])
    async_params = json.loads(request.form['async_params']) if async else None
    try:
        vm_id = create_vm(owner, stats, async=async, async_params=async_params)
    except errors.ResourceNotAvailableError:
        return jsonify({"status": "ResourceNotAvailable"})
    except errors.QueueFull:
        return jsonify({"status": "QueueFull"})
    else:
        return jsonify({"status": "ok", "id": vm_id})

@http_app.route('/cluster/')
def cluster():
    nodes = []
    for spawner in spawners:
        nodes.append({'address': spawner.socket.getpeername(), 'resources': spawner.estimates})

    return jsonify({"status": "ok", "nodes": nodes})

def run_http_app():
    wsgi = wsgiserver.WSGIPathInfoDispatcher({'/': http_app})
    server = wsgiserver.CherryPyWSGIServer(('localhost', 10002), wsgi)
    server.start()

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

    def create_vm_if_possible(self, request: VmCreationRequest):
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

    def check_estimates(self, request):
        for k, v in self.estimates.items():
            if request.stats[k] > v:
                return False
        return True

    def check_and_update_estimates(self, request):
        # Check if spawner has enough resource that
        # it can handle `request`. If it has decrease
        # its resource estimates.
        if not self.estimates:
            return False

        with self.estimate_lock:
            if not self.check_estimates(request):
                return False

            for k, v in self.estimates.items():
                self.estimates[k] = v - request.stats[k]

            return True

    def _write_spawn_request(self, id, request):
        with self.write_lock:
            data = dict({'owner': request.owner, 'stats': request.stats, 'res_id': request.res_id, 'id': id})
            self.file.write("%s\n" %
                            json.dumps(data))
            self.file.flush()

    def _socket_read_loop(self):
        try:
            while True:
                self._socket_read_one()
                self._maybe_unqueue()
        except errors.ConnectionError:
            pass
        finally:
            self.close()

    def _maybe_unqueue(self):
        create_queue.maybe_unqueue(self)

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
    import django
    django.setup()

    logging.basicConfig(level=logging.INFO)
    create_queue.start()
    threading.Thread(target=run_http_app).start()
    spawners_loop()
