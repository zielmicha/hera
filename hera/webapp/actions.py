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

    return '/account/'
