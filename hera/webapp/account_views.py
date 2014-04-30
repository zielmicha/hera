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

class UserBilling(BaseView):
    template_name = "account_base.html"

class BaseAccountView(BaseView):
    def dispatch(self, request, account, *args, **kwargs):
        self.account_name = account
        return BaseView.dispatch(self, request, *args, **kwargs)

class AccountOverview(BaseAccountView):
    template_name = "account_overview.html"

    def get_context_data(self, **kwargs):
        context = BaseAccountView.get_context_data(self, **kwargs)
        context['recent_vms'] = self.get_recent_vm()
        return context

    def get_recent_vm(self):
        ress = models.DerivativeResource.objects.filter(owner=self.account,
                                                        user_type='vm').order_by('-expiry')[:20]
        return ress

class AccountAPI(BaseAccountView):
    template_name = "account_api.html"

    def post(self, *args, **kwargs):
        self.account.regen_api_key()
        self.account.save()
        return self.get(*args, **kwargs)

class AccountTemplates(BaseAccountView):
    template_name = "account_templates.html"

    def get_context_data(self, **kwargs):
        context = BaseAccountView.get_context_data(self, **kwargs)
        context['templates'] = self.account.templates.all()
        return context
