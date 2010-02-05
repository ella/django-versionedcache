from helpers import CachetestCase

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
