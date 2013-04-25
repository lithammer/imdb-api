# -*- coding: utf-8 -*-

import os

from werkzeug.contrib.cache import MemcachedCache, NullCache
import pylibmc

DEBUG = True
CACHE_TIMEOUT = 60 * 24 * 7
CACHE = NullCache()

# Prod specific settings
if os.environ.get('HEROKU'):
    DEBUG = False
    CACHE = MemcachedCache(pylibmc.Client(
        servers=[os.environ.get('MEMCACHIER_SERVERS', 'localhost')],
        username=os.environ.get('MEMCACHIER_USERNAME', None),
        password=os.environ.get('MEMCACHIER_PASSWORD', None),
        binary=True))
