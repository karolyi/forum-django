from django.conf.urls import include, url
from django.contrib import admin
from django.views.i18n import javascript_catalog
from base.views import home

urlpatterns = [
    # Examples:
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', home, name='home'),

    # JavaScript i18n
    url(r'^jsi18n/$', javascript_catalog, kwargs={
        'domain': 'django'
        # Django takes django.conf if this is not specified
        # 'packages': ('webmaster_stats',),
    }),
]
