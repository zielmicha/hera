import requests
import httplib
import json
import io
import os

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
            self._closed = False

        @property
        def websocket_conn(self):
            if self._closed:
                raise IOError('Connection closed')
            if not self._websocket_conn:
                url = self.urls['websocket']
                self._websocket_conn = websocket.create_connection(url)
            return self._websocket_conn

        def upload(self, data):
            return self._upload(io.BytesIO(data), len(data))

        def upload_file(self, file_obj_or_name, size=None):
            if isinstance(file_obj_or_name, str):
                if not size:
                    size = os.path.getsize(file_obj_or_name)
                fileobj = open(file_obj_or_name, 'r')
            else:
                fileobj = file_obj_or_name
                assert size is not None

            return self._upload(fileobj, size)

        def _upload(self, stream, size):
            if self._websocket_conn:
                raise IOError('Websocket connection alread opened - cannot upload via HTTP')
            self._closed = True
            conn, path = self._make_connection(self.urls['http'])
            conn.putrequest('POST', path)
            conn.putheader('Content-Length', size)
            conn.endheaders()
            while size > 0:
                data = stream.read(min(size, 4096))
                if not data:
                    raise IOError('incomplete read from upload source')
                conn.send(data)
                size -= len(data)
            return conn.getresponse()

        def _make_connection(self, url):
            proto, rest = url.split('://', 1)
            if proto == 'http':
                clazz = httplib.HTTPConnection
            elif proto == 'https':
                clazz = httplib.HTTPSConnection
            else:
                raise ValueError('unknown protocol %r' %  proto)
            host, _, path = rest.partition('/')
            return clazz(host), '/' + path

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
