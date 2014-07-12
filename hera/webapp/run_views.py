from django.views.generic import TemplateView
from hera.webapp import models

import json

class BaseView(TemplateView):
    def get_context_data(self):
        return super(BaseView, self).get_context_data()

    def dispatch(self, request, ident, *args, **kwargs):
        self.terminal_request = models.TerminalRequest.objects.get(id=ident)
        self.terminal_request.vm.creator.is_privileged(request.user)
        return super(BaseView, self).dispatch(request, *args, **kwargs)

class MainView(BaseView):
    template_name = 'run_main.html'

    def get_context_data(self):
        data = super(MainView, self).get_context_data()
        data['streams'] = json.dumps(self.terminal_request.streams)
        return data
