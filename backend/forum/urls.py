from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.views.i18n import JavaScriptCatalog
from forum.accounts import urls as urls_accounts
from forum.base import urls as urls_base
from rest_api import urls as urls_api

forum_urlpatterns = [
    url(r'^api/', include(
        urls_api, namespace='rest-api', app_name='forum_rest_api')),
    url(r'^accounts/', include(
        urls_accounts, namespace='accounts', app_name='forum_accounts')),

    # url(r'^jsi18n/$', JavaScriptCatalog.as_view(domain='django'),
    #     name='javascript-catalog'),
    url(r'^', include(urls_base, namespace='base', app_name='base')),
]

urlpatterns = [
    url(r'^', include(forum_urlpatterns, namespace='forum', app_name='forum')),
    url(r'^admin/', include(admin.site.urls)),
    # JavaScript i18n
    url(r'^jsi18n/$', JavaScriptCatalog.as_view(), name='javascript-catalog'),
]

if settings.DEBUG:
    # Add debug toolbar
    import debug_toolbar
    urlpatterns += [url(r'^__debug__/', include(debug_toolbar.urls))]
