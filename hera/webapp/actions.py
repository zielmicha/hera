from hera import models as hera_models
from hera.webapp import models as webapp_models
from django.core.exceptions import PermissionDenied
import heraclient

def clone(account, template):
    if not template.is_privileged(account, 'read'):
        raise PermissionDenied()

    s = heraclient.Sandbox.create(
        timeout=600,
        disk=str(template.id),
        memory=128,
        auth=account.api_auth)

    return attach(account, s.id)

def attach(account, vmid):
    s = heraclient.Sandbox(vmid, auth=account.api_auth)
    proc = s.execute(['bash'], pty_size=(24, 80))
    streams = {'stdout': proc.stdout.urls, 'stdin': proc.stdin.urls}
    vm = hera_models.VM.objects.get(vm_id=vmid)
    request = webapp_models.TerminalRequest(vm=vm, streams=streams)
    request.save()
    return '/run/%d/' % request.id

def attach_by_user(user, vm_id):
    vm = hera_models.VM.objects.get(vm_id=vm_id)
    account = vm.get_privileged_account(user)
    return attach(account, vm_id)
