from hera import accounting
from hera import models
from hera import settings

from django.core import signing

import requests
import json
import socket

CALL_TIMEOUT = 600 # seconds # <-- TODO: warn in docs

class Session:
    def __init__(self):
        pass

    def create_sandbox(self, owner, memory, timeout, disk):
        owner = self.verify_owner(owner)
        disk = self.verify_disk(disk)
        if timeout > 600:
            raise ValueError('unsafely big timeout - TODO: add timeout in vm creation')

        data = {
            'owner': owner,
            'stats': json.dumps({
                'memory': memory,
                'timeout': timeout,
                'disk': disk,
            }),
        }
        resp = requests.post(settings.DISPATCHER_HTTP + 'createvm',
                             data=data)
        resp = json.loads(resp.text)

        if resp["status"] == 'ok':
            info = resp['id']
            vm = models.VM(vm_id=info[0], address=','.join(map(str, info[1:])))
            vm.save()
            return {'status': 'ok', 'id': vm.vm_id}
        else:
            return resp

    def sandbox_action(self, id, args):
        vm = models.VM.objects.get(vm_id=id)
        # TODO: verify permissions
        try:
            ret = vm_call(vm.address, args)
        except ConnectionRefusedError:
            return {'status': 'SandboxNoLongerAlive'}
        return ret

    def verify_owner(self, owner):
        return '_' + owner

    def verify_disk(self, disk):
        if disk.startswith('new,'):
            return disk
        else:
            return None

def vm_call(addr, args, expect_response=True):
    host, port, secret = addr.split(',')
    sock = socket.socket()
    sock.settimeout(CALL_TIMEOUT)
    sock.connect((host, int(port)))

    sock.sendall((secret + '\n').encode())
    sock.sendall((json.dumps(args) + '\n').encode())

    file = sock.makefile('r', 1)
    if expect_response:
        response = file.readline()
        if not response:
            raise ConnectionRefusedError()
        return json.loads(response)
