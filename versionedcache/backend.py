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

class HerdMixin(object):
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
            super(HerdMixin, self).set(key, value, delay)
            # ... and return the default so that the caller will regenerate the cache
            return EXPIRED
        return value


    def add(self, key, value, timeout=0, **kwargs):
        if isinstance(value, unicode):
            value = value.encode('utf-8')
        return super(HerdMixin, self).add(key, *self._tag_value(value, timeout), **kwargs)

    def get(self, key, default=None, **kwargs):
        val = super(HerdMixin, self).get(key, EXPIRED, **kwargs)

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
        super(HerdMixin, self).set(key, *self._tag_value(value, timeout), **kwargs)

    def set_many(self, data, timeout=0, **kwargs):
        new_data = dict((k, self._tag_value(v, timeout)[0]) for k, v in data.items())
        return super(HerdMixin, self).set_many(new_data, timeout, **kwargs)

    def get_many(self, keys, **kwargs):
        out = {}
        for k, v in super(HerdMixin, self).get_many(keys, **kwargs).items():
            if isinstance(v, CacheValue):
                v = self._check_herd_protection(k, *v)
                if v is EXPIRED:
                    continue
            out[k] = v
        return out

    def incr(self, key, delta=1, **kwargs):
        return base.BaseCache.incr(self, key, delta, **kwargs)

    def decr(self, key, delta=1, **kwargs):
        return base.BaseCache.decr(self, key, delta, **kwargs)

class VersionHerdMixin(HerdMixin):
    def __init__(self, server, params):
        if 'version' in params:
            params.setdefault('VERSION', params.pop('version'))
        super(VersionHerdMixin, self).__init__(server, params)

class CacheClass(HerdMixin, memcached.CacheClass):
    pass
