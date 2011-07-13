from django.core.signals import request_finished
from django.core.cache.backends import dummy

from versionedcache import backend

READ_METHODS = ('get', 'get_many', 'has_key' )
WRITE_METHODS = ('set', 'set_many', 'delete', 'add',)

class CacheClass(object):
    def __init__(self, *args, **kwargs):
        self.__cache = backend.CacheClass(*args, **kwargs)
        self.__dummy_cache = dummy.CacheClass()
        request_finished.connect(self.return_to_normal)
        self.return_to_normal()

    def __getattr__(self, attname):
        return getattr(self._mapping.get(attname, self.__cache), attname)

    def return_to_normal(self, *args, **kwargs):
        self._mapping = {}

    def write_only(self):
        for f in READ_METHODS:
            self._mapping[f] = self.__dummy_cache

    def turn_off(self):
        for f in READ_METHODS + WRITE_METHODS:
            self._mapping[f] = self.__dummy_cache
