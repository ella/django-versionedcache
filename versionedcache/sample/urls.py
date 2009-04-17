from django.conf.urls.defaults import *

from versionedcache.sample import views

urlpatterns = patterns('',
    url(r'^$', views.homepage, name='versionedcache-homepage'),
)

