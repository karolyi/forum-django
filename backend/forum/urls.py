from django.conf.urls import include, url
from django.contrib import admin
from django.views.i18n import JavaScriptCatalog
from base.views.frontend import home, topic
from rest_api import urls as urls_api

urlpatterns = [
    # Examples:
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', home, name='home'),
    url(r'^topic/(?P<topic_slug>[a-z0-9-]+)/$', topic, name='topic'),
    url(r'^topic/(?P<topic_slug>[a-z0-9-]+)/(?P<comment_id>\d+)/$',
        topic, name='topic'),
    url(r'^api/', include(
        urls_api, namespace='rest-api', app_name='rest_api')),

    # JavaScript i18n
    url(r'^jsi18n/$', JavaScriptCatalog.as_view(), name='javascript-catalog'),
    # url(r'^jsi18n/$', JavaScriptCatalog.as_view(domain='django'),
    #     name='javascript-catalog'),
]
