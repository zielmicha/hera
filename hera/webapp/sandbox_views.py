from django.views.generic import TemplateView
from django.utils.functional import cached_property
from django.core.exceptions import PermissionDenied
from hera import models

class BaseSandboxView(TemplateView):
    def dispatch(self, request, sandbox, *args, **kwargs):
        self.sandbox_uuid = sandbox
        return TemplateView.dispatch(self, request, *args, **kwargs)

    @cached_property
    def sandbox(self):
        sandbox = models.VM.objects.get(vm_id=self.sandbox_uuid)
        if not sandbox.creator.is_privileged(self.request.user):
            raise PermissionDenied()
        return sandbox

    @cached_property
    def resource(self):
        return models.DerivativeResource.objects.get(
            user_type='vm',
            user_id=self.sandbox.vm_id)

    def get_context_data(self, **kwargs):
        context = TemplateView.get_context_data(self, **kwargs)
        context['sandbox'] = self.sandbox
        context['resource'] = self.resource
        return context

class Sandbox(BaseSandboxView):
    template_name = 'sandbox.html'
