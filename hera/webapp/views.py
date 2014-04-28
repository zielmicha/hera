from django.views.generic import TemplateView
from django.utils.functional import cached_property
from hera import models

class BaseView(TemplateView):
    def get_context_data(self, **kwargs):
        context = TemplateView.get_context_data(self, **kwargs)
        context['account'] = self.account
        return context

    @cached_property
    def account(self):
        account = getattr(self, 'account_name', None)
        if not account:
            account = str(self.request.user)
        account = models.Account.get_account(account)
        if not account.is_privileged(self.request.user):
            account = models.Account.get_account(str(self.request.user))
            if not account.is_privileged(self.request.user):
                raise Exception('not privileged to access itself?')
            return account
        else:
            return account

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
        return context

    def post(self, *args, **kwargs):
        self.account.regen_api_key()
        self.account.save()
        return self.get(*args, **kwargs)
