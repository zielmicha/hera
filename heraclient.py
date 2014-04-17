import requests
import json
import io

URL = 'http://localhost:8080/'

class Sandbox(object):
    def __init__(self, id):
        self.id = id

    @classmethod
    def create(self, timeout, disk, owner='me', memory=128):
        if isinstance(disk, Template):
            disk = disk.id
        assert isinstance(memory, int)
        assert isinstance(timeout, (int, float))
        assert isinstance(disk, str)
        resp = requests.post(URL + 'sandbox/', data={
            'owner': owner,
            'timeout': timeout,
            'disk': disk,
            'memory': memory,
        })
        response_raise(resp)
        resp = resp.json()
        return Sandbox(resp['id'])

    def save_as_template(self, name=None):
        assert isinstance(name, (type(None), str))
        resp = self.action('create_template', name=name)
        return Template(resp['id'])

    def execute(self, args, sync=False, chroot=True, shell=False,
                stderr_to_stdout=False):
        '''
        Execute process in sandbox.
        '''
        kwargs = dict(sync='true' if sync else 'false',
                      chroot=chroot)
        if shell:
            assert isinstance(args, str)
            kwargs['command'] = args
        else:
            assert all( isinstance(param, str) for param in args )
            kwargs['args'] = json.dumps(args)

        if stderr_to_stdout:
            kwargs['stderr'] = 'stdout'

        resp = self.action('exec', **kwargs)
        return Process(resp, sync=sync)

    def action(self, type, **args):
        resp = requests.post(URL + 'sandbox/%s/%s' % (self.id, type), data=args)
        response_raise(resp)
        return resp.json()

class Process(object):
    def __init__(self, resp, sync):
        self.resp = resp
        self.sync = sync
        if not self.sync:
            self.stdin = Stream(resp['stdin'])
            if resp['stdin'] == resp['stdout']:
                self.stdout = self.stdin
            else:
                self.stdout = Stream(resp['stdout'])
            if 'stderr' in resp:
                self.stderr = Stream(resp['stderr'])

    def read_stdout(self):
        return self._read_stream('stdout')

    def read_stderr(self):
        return self._read_stream('stderr')

    def _read_stream(self, name):
        if self.sync:
            return self.resp[name]
        else:
            raise NotImplementedError()

class Template(object):
    def __init__(self, id):
        self.id = id

def response_raise(resp):
    resp.raise_for_status()
    resp = resp.json()
    if resp.get('status') != 'ok':
        msg = 'Service returned error %r.' % resp.get('status')
        stacktrace = resp.get('stacktrace')
        if stacktrace:
            msg += '\n' + stacktrace
        raise ApiError(msg)

def new_disk(size):
    return 'new,%s' % size

class ApiError(Exception):
    pass

# Websocket streams

class _StreamBase(io.RawIOBase):
    def __init__(self, urls):
        self.urls = urls

try:
    import websocket
except ImportError as err:
    import_error = err
    class Stream(_StreamBase):
        def read(self, n=None):
            raise import_error

        def write(self, data):
            raise import_error
else:
    class Stream(_StreamBase):
        def __init__(self, urls):
            _StreamBase.__init__(self, urls)
            self._websocket_conn = None

        @property
        def websocket_conn(self):
            if not self._websocket_conn:
                url = self.urls['websocket']
                self._websocket_conn = websocket.create_connection(url)
            return self._websocket_conn

        def read(self, n=2**32):
            buff = []
            length_left = n
            while length_left > 0:
                data = self.websocket_conn.recv()
                if not data:
                    break
                buff.append(data)
                length_left -= len(buff)
            return ''.join(buff)

        def write(self, data):
            self.websocket_conn.send(data)
