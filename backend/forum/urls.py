from django.conf.urls import include, url
from django.contrib import admin
from django.views.i18n import JavaScriptCatalog
from base.views import home

urlpatterns = [
    # Examples:
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', home, name='home'),

    # JavaScript i18n
    url(r'^jsi18n/$', JavaScriptCatalog.as_view(domain='django'),
        name='javascript-catalog'),
]
