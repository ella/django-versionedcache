from django.core.cache.backends import locmem
from versionedcache.backend import VersionHerdMixin

class CustomBackend(locmem.CacheClass):
    def set_many(self, data, *args, **kwargs):
        for k, v in data.items():
            self.set(k, v, *args, **kwargs)

class CacheClass(VersionHerdMixin, CustomBackend):
    pass


