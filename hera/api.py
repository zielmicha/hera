from hera import accounting
from hera import models
from hera import settings

from django.core import signing

import requests
import json

class Session:
    def __init__(self):
        pass

    def create_sandbox(self, owner, memory, timeout, disk):
        owner = self.verify_owner(owner)
        disk = self.verify_disk(disk)
        if timeout > 60:
            raise ValueError('unsafely big timeout - TODO: add timeout in vm creation')

        data = {
            'owner': owner,
            'stats': json.dumps({
                'memory': memory,
                'timeout': timeout,
            })
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

    def sandbox_action(self, id, ):
        pass

    def verify_owner(self, owner):
        return '_' + owner

    def verify_disk(self, disk):
        return None
