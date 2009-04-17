# -*- coding: utf-8 -*-
import time 

from nose import SkipTest
from djangosanetesting import UnitTestCase

from django.core.cache import cache

from versionedcache import backend

class CachetestCase(UnitTestCase):
    def setUp(self):
        super(CachetestCase, self).setUp()
        if not isinstance(cache, backend.CacheClass):
            raise SkipTest

    def tearDown(self):
        cache._cache.flush_all()

class TestMintCache(CachetestCase):
    def test_return_default_on_empty_cache(self):
        self.assert_equals('DEFAULT', cache.get('non-existent-key', 'DEFAULT'))

    def test_return_None_on_empty_cache(self):
        self.assert_equals(None, cache.get('non-existent-key'))

    def test_set_sets_cache(self):
        cache.set('cache-key', 'cache value')
        self.assert_equals('cache value', cache.get('cache-key'))

    def test_cache_expires(self):
        cache.set('cache-key', 'cache value', timeout=0.1)
        time.sleep(0.1)
        self.assert_equals(None, cache.get('cache-key'))

    def test_cache_stales_only_once_after_some_time(self):
        cache.set('cache-key', 'cache value', timeout=4)
        time.sleep(3.5)
        self.assert_equals(None, cache.get('cache-key'))
        self.assert_equals('cache value', cache.get('cache-key'))

class TestVersioning(CachetestCase):
    def test_version_separation(self):
        from django.conf import settings
        cache.set('cache-key', 'cache value')
        settings.VERSION += 'NEW'
        self.assert_equals(None, cache.get('cache-key'))
