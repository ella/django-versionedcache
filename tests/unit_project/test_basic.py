# -*- coding: utf-8 -*-
import time 

from djangosanetesting import UnitTestCase

from django.core.cache import cache

from versionedcache import backend

class CachetestCase(UnitTestCase):
    def setUp(self):
        super(CachetestCase, self).setUp()
        if not isinstance(cache, backend.CacheClass):
            raise self.SkipTest()

    def tearDown(self):
        cache._cache.flush_all()

class TestMintCache(CachetestCase):
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

class TestMethods(CachetestCase):
    def test_incr_works(self):
        cache.set('key', 0)
        cache.incr('key')
        self.assert_equals(1, cache.get('key'))

    def test_decr_works(self):
        cache.set('key', 10)
        cache.decr('key')
        self.assert_equals(9, cache.get('key'))

    def test_incr_throws_error_on_non_existing_key(self):
        self.assert_raises(ValueError, cache.incr, 'non-existent-key')

    def test_add_doesnt_set_cache_if_present(self):
        cache.set('cache-key', 'original cache value')
        x = cache.add('cache-key', 'cache value')
        self.assert_equals(False, x)
        self.assert_equals('original cache value', cache.get('cache-key'))

    def test_add_sets_cache_if_none_present(self):
        x = cache.add('cache-key', 'cache value')
        self.assert_equals(True, x)
        self.assert_equals('cache value', cache.get('cache-key'))

    def test_get_returns_default_on_empty_cache(self):
        self.assert_equals('DEFAULT', cache.get('non-existent-key', 'DEFAULT'))

    def test_get_returns_None_on_empty_cache(self):
        self.assert_equals(None, cache.get('non-existent-key'))

    def test_set_sets_cache(self):
        cache.set('cache-key', 'cache value')
        self.assert_equals('cache value', cache.get('cache-key'))

    def test_add_works_with_unicode(self):
        un = u"你好 category"
        cache.add('cache-key', un)
        self.assert_equals(un, cache.get('cache-key'))

    def test_set_works_with_unicode(self):
        un = u"你好 category"
        cache.set('cache-key', un)
        self.assert_equals(un, cache.get('cache-key'))

    def test_get_many(self):
        cache.set('cache-key', 'cache value')
        self.assert_equals({'cache-key': 'cache value'}, cache.get_many(['cache-key', 'non-existent-key']))


