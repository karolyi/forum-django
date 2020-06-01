from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static
from django.contrib.admin.sites import site
from django.urls.conf import include, path

from forum.account.urls import urlpatterns_account
from forum.base.urls import urlpatterns_base
from forum.rest_api.urls import urlpatterns_api

forum_urlpatterns = [
    url(regex=r'^api/', view=include(arg=(urlpatterns_api, 'rest-api'),
        namespace='rest-api')),
    url(regex=r'^account/', view=include(arg=(urlpatterns_account, 'account'),
        namespace='account')),
    url(regex=r'^', view=include(arg=(urlpatterns_base, 'base'),
        namespace='base')),
]

urlpatterns = [
    url(regex=r'^admin/', view=site.urls),
    url(regex=r'^', view=include(
        arg=(forum_urlpatterns, 'forum'), namespace='forum')),
]

if settings.DEBUG:
    # Add debug toolbar
    import debug_toolbar
    urlpatterns += [
        path(route='__debug__/', view=include(arg=debug_toolbar.urls))]
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
