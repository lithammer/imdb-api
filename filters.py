# -*- coding: utf-8 -*-

import os
from functools import wraps

from flask import request, current_app
from werkzeug.contrib.cache import MemcachedCache
import pylibmc

CACHE_TIMEOUT = 60 * 24 * 7

cache = MemcachedCache(pylibmc.Client(
    servers=[os.environ.get('MEMCACHE_SERVERS', 'localhost')],
    username=os.environ.get('MEMCACHE_USERNAME', None),
    password=os.environ.get('MEMCACHE_PASSWORD', None),
    binary=True
    )
)


def support_jsonp(f):
    """ Wraps JSONified output for JSONP """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        callback = request.args.get('callback', False)
        if callback:
            content = str(callback) + '(' + str(f(*args, **kwargs).data) + ')'
            return current_app.response_class(
                    content, mimetype='application/javascript')
        else:
            return f(*args, **kwargs)
    return decorated_function


def cached(f, timeout=None):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # timeout = timeout or CACHE_TIMEOUT
        response = cache.get(request.path)
        if response is None:
            response = f(*args, **kwargs)
            cache.set(request.path, response, timeout or CACHE_TIMEOUT)
        return response
    return decorated_function
