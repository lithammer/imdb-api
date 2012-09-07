# -*- coding: utf-8 -*-

import os

from werkzeug.contrib.cache import MemcachedCache, NullCache
import pylibmc

DEBUG = True
CACHE_TIMEOUT = 60 * 24 * 7
CACHE = NullCache()

# Prod specific settings
if os.environ.get('HEROKU'):
    DEBUG = True
    CACHE = MemcachedCache(pylibmc.Client(
        servers=[os.environ.get('MEMCACHE_SERVERS', 'localhost')],
        username=os.environ.get('MEMCACHE_USERNAME', None),
        password=os.environ.get('MEMCACHE_PASSWORD', None),
        binary=True))
