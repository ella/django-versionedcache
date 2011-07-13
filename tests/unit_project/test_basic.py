# -*- coding: utf-8 -*-
import time

from django.core.cache import get_cache
from django.conf import settings


from helpers import CachetestCase

class TestMintCache(CachetestCase):
    def test_cache_expires(self):
        self.cache.set('cache-key', 'cache value', timeout=0.1)
        time.sleep(0.1)
        self.assert_equals(None, self.cache.get('cache-key'))

    def test_cache_stales_only_once_after_some_time(self):
        self.cache.set('cache-key', 'cache value', timeout=.4)
        time.sleep(.35)
        self.assert_equals(None, self.cache.get('cache-key'))
        self.assert_equals('cache value', self.cache.get('cache-key'))

class TestVersioning(CachetestCase):
    def test_version_separation(self):
        self.cache.set('cache-key', 'cache value')
        settings.CACHE_BACKEND += '?version=NEW'
        self.cache = get_cache(settings.CACHE_BACKEND)
        self.assert_equals(None, self.cache.get('cache-key'))

class TestMethods(CachetestCase):
    def test_incr_works(self):
        self.cache.set('key', 0)
        self.cache.incr('key')
        self.assert_equals(1, self.cache.get('key'))

    def test_decr_works(self):
        self.cache.set('key', 10)
        self.cache.decr('key')
        self.assert_equals(9, self.cache.get('key'))

    def test_incr_throws_error_on_non_existing_key(self):
        self.assert_raises(ValueError, self.cache.incr, 'non-existent-key')

    def test_add_doesnt_set_cache_if_present(self):
        self.cache.set('cache-key', 'original cache value')
        x = self.cache.add('cache-key', 'cache value')
        self.assert_equals(False, x)
        self.assert_equals('original cache value', self.cache.get('cache-key'))

    def test_add_sets_cache_if_none_present(self):
        x = self.cache.add('cache-key', 'cache value')
        self.assert_equals(True, x)
        self.assert_equals('cache value', self.cache.get('cache-key'))

    def test_get_returns_default_on_empty_cache(self):
        self.assert_equals('DEFAULT', self.cache.get('non-existent-key', 'DEFAULT'))

    def test_get_returns_None_on_empty_cache(self):
        self.assert_equals(None, self.cache.get('non-existent-key'))

    def test_set_sets_cache(self):
        self.cache.set('cache-key', 'cache value')
        self.assert_equals('cache value', self.cache.get('cache-key'))

    def test_add_works_with_unicode(self):
        un = u"你好 category"
        self.cache.add('cache-key', un)
        self.assert_equals(un, self.cache.get('cache-key'))

    def test_set_works_with_unicode(self):
        un = u"你好 category"
        self.cache.set('cache-key', un)
        self.assert_equals(un, self.cache.get('cache-key'))

    def test_set_many(self):
        self.cache.set_many({'k': 'value', 'k2': 'other-val'})
        self.assert_equals('value', self.cache.get('k'))
        self.assert_equals('other-val', self.cache.get('k2'))

    def test_get_many(self):
        self.cache.set('cache-key', 'cache value')
        self.cache.set('cache-key-herded', 'cache value II', 0.4)
        time.sleep(0.35)
        self.assert_equals(
            {'cache-key': 'cache value'},
            self.cache.get_many(['cache-key', 'cache-key-herded', 'non-existent-key'])
        )
        self.assert_equals(
            {'cache-key': 'cache value', 'cache-key-herded': 'cache value II'},
            self.cache.get_many(['cache-key', 'cache-key-herded', 'non-existent-key'])
        )

    def test_delete_deletes_versioned_cache(self):
        self.cache.set('key', 10)
        self.cache.delete('key')
        self.assert_equals(None, self.cache.get('key'))

    def test_cache_key_is_not_versioned_twice(self):
        c = get_cache('backend://')
        c.set_many({'a': 42, 'b': 'value'})
        self.assert_equals({'a': 42, 'b': 'value'}, c.get_many(['a', 'b']))
