from django.core import cache

from helpers import CachetestCase, CachetestDatabaseCase

class TestWriteOnlyMethods(CachetestCase):
    def test_write_works_and_cannot_be_read_until_returned_to_normal(self):
        self.cache.write_only()
        self.cache.set('cache-key', 'cache value')
        self.assert_equals(None, self.cache.get('cache-key'))
        self.cache.return_to_normal()
        self.assert_equals('cache value', self.cache.get('cache-key'))

class TestCacheTurnedOff(CachetestCase):
    def test_existing_values_in_cache_not_affected(self):
        self.cache.set('cache-key', 'cache value')
        self.cache.turn_off()
        self.cache.set('cache-key', 'another cache value')
        self.cache.return_to_normal()
        self.assert_equals('cache value', self.cache.get('cache-key'))

class TestCacheDebugMiddleware(CachetestDatabaseCase):
    def test_anonymous_user_gets_normal_cache_behavior(self):
        c = self.client

        c.post('/set/?cache_debug=turn_off', {'key': 'value'})
        self.assert_equals(u'value', cache.cache.get('key'))

        response = c.get('/get/key/', {'cache_debug': 'turn_off'})
        self.assert_equals(repr(u'value'), response.content)

    def test_normal_user_gets_normal_cache_behavior(self):
        c = self.client
        c.login(username='normal', password='secret')

        c.post('/set/?cache_debug=turn_off', {'key': 'value'})
        self.assert_equals(u'value', cache.cache.get('key'))

        response = c.get('/get/key/', {'cache_debug': 'turn_off'})
        self.assert_equals(repr(u'value'), response.content)

    def test_super_user_can_turn_cache_off(self):
        c = self.client
        c.login(username='super', password='supersecret')

        c.post('/set/?cache_debug=turn_off', {'key': 'other value'})
        self.assert_equals(None, cache.cache.get('key'))

    def test_super_user_can_turn_cache_write_only(self):
        c = self.client
        c.login(username='super', password='supersecret')

        cache.cache.set('key', 'some value')

        c.post('/set/?cache_debug=write_only', {'key': 'other value'})
        self.assert_equals('other value', cache.cache.get('key'))

        response = c.get('/get/key/', {'cache_debug': 'write_only'})
        self.assert_equals(repr(None), response.content)
        self.assert_equals('other value', cache.cache.get('key'))

