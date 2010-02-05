from django.core import cache
from django.core.exceptions import MiddlewareNotUsed

from versionedcache.debug import CacheClass

class CacheDebugMiddleware(object):
    def __init__(self):
        if not isinstance(cache.cache, CacheClass):
            raise MiddlewareNotUsed()

    def process_request(self, request):
        if request.user.is_superuser and 'cache_debug' in request.GET:
            action = request.GET['cache_debug']

            # only two actions allowed
            if action not in ('turn_off', 'write_only'):
                return
            
            # implement action
            getattr(cache.cache, action)()

