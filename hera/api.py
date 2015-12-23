from hera import models
from hera import settings

from django.core.exceptions import PermissionDenied

import requests
import json
import socket
import hmac

CALL_TIMEOUT = 600 # seconds # <-- TODO: warn in docs

class Session:
    def __init__(self, account, api_key):
        self.account = models.Account.get_account(account)
        expected = self.account.get_api_key()
        if not hmac.compare_digest(expected, api_key):
            raise PermissionDenied()

    def get_cluster(self):
        return requests.get(settings.DISPATCHER_HTTP + 'cluster').json()

    def create_sandbox(self, owner, memory, timeout, disk, whole_node,
                       async, webhook_url, webhook_secret, priority, priority_growth):
        if not async and (webhook_url or priority or priority_growth):
            return {'status': 'MalformedRequest'}

        owner = self.verify_owner(owner)
        disk = self.verify_disk(disk)
        if timeout > 600: # TODO: add timeout in vm creation
            return {'status': 'TimeoutTooBig'}

        memory = int(memory)

        if memory < 32:
            return {'status': 'NotEnoughMemoryRequested'}

        stats = json.dumps({
            'memory': memory,
            'timeout': timeout,
            'disk': disk,
            'slots': 1000 if whole_node else 1,
        })
        data = {
            'owner': owner.name,
            'stats': stats,
            'async': async
        }
        if async:
            data['async_params'] = json.dumps({
                'webhook_url': webhook_url,
                'webhook_secret': webhook_secret,
                'priority': priority,
                'priority_growth': priority_growth
            })

        resp = requests.post(settings.DISPATCHER_HTTP + 'createvm',
                             data=data)
        resp = json.loads(resp.text)

        if resp["status"] == 'ok':
            return {'status': 'ok', 'id': resp['id']}
        else:
            return resp

    def sandbox_action(self, id, action, args):
        vm = models.VM.objects.get(vm_id=id)
        # TODO: verify permissions
        try:
            ret = self.vm_call(vm, action, args)
        except ConnectionRefusedError:
            return {'status': 'SandboxNoLongerAlive'}
        return ret

    def vm_call(self, vm, action, args):
        return vm_call(vm.address, dict(args, type=action))

    def verify_owner(self, owner):
        if owner == 'me':
            return self.account
        else:
            account = models.Account.objects.get(name=owner)
            if account.name != self.account.name: # TODO: something more sophisticated
                raise PermissionDenied()
            return account

    def verify_disk(self, disk):
        if disk.startswith('new,'):
            return disk
        else:
            return self.get_template(disk, operation='read').id

    def get_template(self, ident, operation):
        try:
            ident_as_int = int(ident)
        except ValueError:
            ident_split = ident.split('/', 1)
            if len(ident_split) == 1:
                account = 'system'
                template_name = ident_split[0]
            else:
                account = ident_split[0]
                template_name = ident_split[1]
            instance = models.Template.objects.get(name=template_name, owner__name=account)
        else:
            instance = models.Template.objects.get(id=ident_as_int)

        if instance.is_privileged(self.account, operation=operation):
            return instance
        else:
            raise PermissionDenied()

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
