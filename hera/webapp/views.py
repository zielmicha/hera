from django.views.generic import TemplateView

class BaseView(TemplateView):
    def get_context_data(self, **kwargs):
        context = TemplateView.get_context_data(self, **kwargs)
        account = getattr(self, 'account_name', None)
        if not account:
            account = str(self.request.user)
        context['account'] = account
        return context

class UserOverview(BaseView):
    template_name = "account_base.html"

class BaseAccountView(BaseView):
    def dispatch(self, request, account, *args, **kwargs):
        self.account_name = account
        return BaseView.dispatch(self, request, *args, **kwargs)

class AccountOverview(BaseAccountView):
    template_name = "account_base.html"

class AccountAPI(BaseAccountView):
    template_name = "account_api.html"

    def get_context_data(self, **kwargs):
        context = BaseAccountView.get_context_data(self, **kwargs)
        context['api_key'] = 'be4e37f1900002c6966ee831efe0f6585fcf50f7'
        return context
