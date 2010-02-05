from django.conf.urls.defaults import *

urlpatterns = patterns('unit_project.views',
    (r'^set/$', 'set'),
    (r'^get/([^/]*)/$', 'get'),
)
