import time
from collections import namedtuple

from django.core.cache.backends import memcached, base
from django.utils.encoding import smart_unicode, smart_str

from django.conf import settings

DEFAULT_TIMEOUT_RATIO = 3.0/4.0
EXPIRED = object()

class CacheKey(str):
    pass
CacheValue = namedtuple('CacheValue', 'value, stale_time, delay')

class VersionHerdMixin(object):
    def __init__(self, server, params):
        self._version = params.pop('version', None)
        super(VersionHerdMixin, self).__init__(server, params)

    def _tag_key(self, key):
        if isinstance(key, CacheKey):
            return key
        return CacheKey(smart_str((self._version or getattr(settings, 'CACHE_VERSION', '')) + smart_str(key)).decode('ascii', 'ignore')[:250])

    def _tag_value(self, value, timeout):
        """
        Add staleness information to the value when setting.

        return value tuple and timeout
        """
        t = timeout or self.default_timeout

        if isinstance(value, CacheValue):
            return value, t

        stale = t * getattr(settings, 'TIMEOUT_RATIO', DEFAULT_TIMEOUT_RATIO)
        stale_time = time.time() + stale
        delay = 2 * (t - stale)
        return CacheValue(value, stale_time, delay), t

    def _check_herd_protection(self, key, value, stale_time, delay):
        # cache is stale, refresh
        if stale_time and stale_time <= time.time():
            # keep the stale value in cache for delay seconds ...
            super(VersionHerdMixin, self).set(key, value, delay)
            # ... and return the default so that the caller will regenerate the cache
            return EXPIRED
        return value


    def add(self, key, value, timeout=0, **kwargs):
        if isinstance(value, unicode):
            value = value.encode('utf-8')
        return super(VersionHerdMixin, self).add(self._tag_key(key), *self._tag_value(value, timeout), **kwargs)

    def get(self, key, default=None, **kwargs):
        key = self._tag_key(key)

        val = super(VersionHerdMixin, self).get(key, EXPIRED, **kwargs)

        # value not in cache
        if val is EXPIRED:
            return default

        if isinstance(val, CacheValue):
            # unpack timeout
            val = self._check_herd_protection(key, *val)

        # herd protection actively refuses me the value, comply
        if val is EXPIRED:
            return default

        # unicode is better than str
        if isinstance(val, basestring):
            return smart_unicode(val)
        else:
            return val

    def set(self, key, value, timeout=0, **kwargs):
        if isinstance(value, unicode):
            value = smart_str(value)
        super(VersionHerdMixin, self).set(self._tag_key(key), *self._tag_value(value, timeout), **kwargs)

    def delete(self, key, *args, **kwargs):
        super(VersionHerdMixin, self).delete(self._tag_key(key), *args, **kwargs)

    def set_many(self, data, timeout=0, **kwargs):
        new_data = dict((self._tag_key(k), self._tag_value(v, timeout)[0]) for k, v in data.items())
        return super(VersionHerdMixin, self).set_many(new_data, timeout, **kwargs)

    def get_many(self, keys, **kwargs):
        key_map = dict((self._tag_key(k), k) for k in keys)
        out = {}
        for k, v in super(VersionHerdMixin, self).get_many(key_map.keys(), **kwargs).items():
            if isinstance(v, CacheValue):
                v = self._check_herd_protection(k, *v)
                if v is EXPIRED:
                    continue
            out[key_map[k]] = v
        return out

    def incr(self, key, delta=1, **kwargs):
        return base.BaseCache.incr(self, key, delta, **kwargs)

    def decr(self, key, delta=1, **kwargs):
        return base.BaseCache.decr(self, key, delta, **kwargs)

class CacheClass(VersionHerdMixin, memcached.CacheClass):
    pass
