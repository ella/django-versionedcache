import time

from django.core.cache.backends import memcached, base
from django.utils.encoding import smart_unicode, smart_str

from django.conf import settings

DEFAULT_TIMEOUT_RATIO = 3.0/4.0

class CacheClass(memcached.CacheClass):

    def __init__(self, server, params):
        self._version = params.get('version', None)
        super(CacheClass, self).__init__(server, params)

        self._tune_server()

    def _tune_server(self):
        '''
        set some connection-related properties to memcache server
        (expects python-memcached bindings)
        '''
        if not (hasattr(settings, 'MEMCACHE_TUNE') and type(settings.MEMCACHE_TUNE) == dict):
            return

        if not (self._cache and hasattr(self._cache, 'servers')):
            return

        props = ('_SOCKET_TIMEOUT', '_DEAD_RETRY')
        tune_props = {}
        for prop in props:
            if prop in settings.MEMCACHE_TUNE.keys():
                tune_props[prop] = settings.MEMCACHE_TUNE[prop]

        for server in self._cache.servers:
            for prop in tune_props:
                if not hasattr(server, prop):
                    # if it's missing in one server, others will miss it probably too
                    del tune_props[prop]
                    continue

                if hasattr(tune_props[prop], '__call__'):
                    prop_val = tune_props[prop].__call__()
                else:
                    prop_val = tune_props[prop]

                #  we don't want to use non-numeric values
                if type(prop_val) not in (int, float):
                    del tune_props[prop]
                    continue

                setattr(server, prop, prop_val)


    def _tag_key(self, key):
        return str(smart_str((self._version or getattr(settings, 'CACHE_VERSION', '')) + smart_str(key)).decode('ascii', 'ignore')[:250])

    def _tag_value(self, value, timeout):
        """
        Add staleness information to the value when setting.

        return value tuple and timeout
        """
        t = timeout or self.default_timeout
        stale = t * getattr(settings, 'TIMEOUT_RATIO', DEFAULT_TIMEOUT_RATIO)
        stale_time = time.time() + stale
        delay = 2 * (t - stale)
        return (value, stale_time, delay), t

    def add(self, key, value, timeout=0):
        if isinstance(value, unicode):
            value = value.encode('utf-8')
        return self._cache.add(self._tag_key(key), *self._tag_value(value, timeout))
 
    def get(self, key, default=None):
        key = self._tag_key(key)

        val = self._cache.get(key)

        if val:
            # unpack timeout
            val, stale_time, delay = val

            # cache is stale, refresh
            if stale_time and stale_time <= time.time():
                # keep the stale value in cache for delay seconds ...
                self._cache.set(key, (val, None, 0), delay)
                # ... and return the default so that the caller will regenerate the cache
                return default

        if val is None:
            return default
        else:
            if isinstance(val, basestring):
                return smart_unicode(val)
            else:
                return val 
 
    def set(self, key, value, timeout=0):
        if isinstance(value, unicode):
            value = smart_str(value)
        self._cache.set(self._tag_key(key), *self._tag_value(value, timeout))

    def delete(self, key, *args, **kwargs):
        super(CacheClass, self).delete(self._tag_key(key), *args, **kwargs)
 
    def get_many(self, keys):
        key_map = dict((self._tag_key(k), k) for k in keys)
        return dict( (key_map[k], v[0]) for (k,v) in super(CacheClass, self).get_many(key_map.keys()).items())
 
    def incr(self, key, delta=1):
        return base.BaseCache.incr(self, key, delta)
 
    def decr(self, key, delta=1):
        return base.BaseCache.decr(self, key, delta)

