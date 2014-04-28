from django.conf.urls import include, url, patterns
from django.contrib import admin
from django.conf.urls.static import static
from django.conf import settings
from django.views.generic import RedirectView, TemplateView
from hera.webapp import views

admin.autodiscover()

urlpatterns = patterns('',
                       url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
                       url(r'^admin/', admin.site.urls),
                       url(r'^accounts/', include('registration.backends.simple.urls')),
                       url(r'^accounts/profile', RedirectView.as_view(url='/account')),
                       url(r'^account$', RedirectView.as_view(url='/account/')),
                       url(r'^users/', RedirectView.as_view(url='/account')),
                       url(r'^$', TemplateView.as_view(template_name='main.html')),
                       url(r'^account/$', views.UserOverview.as_view()),
                       url(r'^account/(.+)/overview$', views.AccountOverview.as_view()),
                       url(r'^account/(.+)/api$', views.AccountAPI.as_view(),)
) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
