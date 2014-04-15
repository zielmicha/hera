import requests
import json

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

    def execute(self, sync=False, chroot=True, args=None, command=None,
                stderr_to_stdout=False,):
        if command:
            assert isinstance(command, str)
            assert not args
        elif args:
            assert all( isinstance(param, str) for param in args )
        else:
            raise ValueError('expected either `command` or `args` argument')
        kwargs = dict(sync='true' if sync else 'false',
                      chroot=chroot)
        if args:
            kwargs['args'] = json.dumps(args)
        if command:
            kwargs['command'] = command
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
