from django.conf.urls.defaults import *

urlpatterns = patterns('test_versionedcache.views',
    (r'^set/$', 'set'),
    (r'^get/([^/]*)/$', 'get'),
)
