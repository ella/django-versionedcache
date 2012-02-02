from unittest import TestCase as UnitTestCase
from django.test import TestCase

from django.core import cache
from django.conf import settings
from django.contrib.auth.models import User
from django.core.signals import request_finished

from versionedcache import backend, debug

from nose import SkipTest

class CachetestCase(UnitTestCase):
    def setUp(self):
        super(CachetestCase, self).setUp()
        self.cache = cache.get_cache(settings.CACHE_BACKEND)
        if not isinstance(self.cache, (debug.CacheClass, backend.CacheClass)):
            raise SkipTest()

    def tearDown(self):
        self.cache._cache.flush_all()


class CachetestDatabaseCase(TestCase):
    def setUp(self):
        super(CachetestDatabaseCase, self).setUp()
        cache.cache = cache.get_cache(settings.CACHE_BACKEND)
        if not isinstance(cache.cache, (debug.CacheClass, backend.CacheClass)):
            raise self.SkipTest()

        User.objects.create_user('normal', 'hello@there.com', 'secret')
        User.objects.create_superuser('super', 'hello@there.com', 'supersecret')

    def tearDown(self):
        super(CachetestDatabaseCase, self).tearDown()
        cache.cache._cache.flush_all()
        request_finished.receivers = []






