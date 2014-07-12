from django.views.generic import TemplateView

class BaseView(TemplateView):
    def get_context_data(self):
        pass

    def dispatch(self, request, ident, *args, **kwargs):
        return super(BaseView, self).dispatch(request, *args, **kwargs)


class MainView(BaseView):
    pass
