from djangosanetesting import UnitTestCase

from django.core.cache import get_cache
from django.conf import settings

from versionedcache import backend, debug

class CachetestCase(UnitTestCase):
    def setUp(self):
        super(CachetestCase, self).setUp()
        self.cache = get_cache(settings.CACHE_BACKEND)
        if not isinstance(self.cache, (debug.CacheClass, backend.CacheClass)):
            raise self.SkipTest()

    def tearDown(self):
        self.cache._cache.flush_all()


