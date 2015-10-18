from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.views.i18n import javascript_catalog

urlpatterns = patterns(
    '',
    # Examples:
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', 'base.views.home', name='home'),

    # JavaScript i18n
    url(r'^jsi18n/$', javascript_catalog, kwargs={
        'domain': 'django'
        # Django takes django.conf if this is not specified
        # 'packages': ('webmaster_stats',),
    }),
)
