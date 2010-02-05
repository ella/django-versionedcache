from django.core import cache
from django import http

def get(request, key):
    return http.HttpResponse(repr(cache.cache.get(key)))

def set(request):
    print cache.cache._mapping
    for key, value in request.POST.items():
        cache.cache.set(key, value)
    return http.HttpResponse('')

