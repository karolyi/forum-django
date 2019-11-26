from django.conf import settings
from django.conf.urls import url
from django.contrib import admin
from django.urls.conf import include
from django.views.i18n import JavaScriptCatalog

from forum.account import urls as urls_account
from forum.base import urls as urls_base
from forum.rest_api import urls as urls_api

forum_urlpatterns = [
    url(regex=r'^api/', view=include(
        arg=(urls_api, 'rest-api'), namespace='rest-api')),
    url(regex=r'^account/', view=include(
        arg=(urls_account, 'account'), namespace='account')),

    # url(regex=r'^jsi18n/$', JavaScriptCatalog.as_view(domain='django'),
    #     name='javascript-catalog'),
    url(regex=r'^', view=include(arg=(urls_base, 'base'), namespace='base')),
]

urlpatterns = [
    url(regex=r'^admin/', view=admin.site.urls),
    # JavaScript i18n
    url(regex=r'^jsi18n/$',
        view=JavaScriptCatalog.as_view(), name='javascript-catalog'),
    url(regex=r'^', view=include(
        arg=(forum_urlpatterns, 'forum'), namespace='forum')),
]

if settings.DEBUG:
    # Add debug toolbar
    import debug_toolbar
    urlpatterns += [
        url(regex=r'^__debug__/', view=include(arg=debug_toolbar.urls))]
