import os

try:
    import urlparse
except ImportError:
    import urllib.parse as urlparse

import dj_database_url
from werkzeug.contrib.cache import RedisCache, NullCache

here = os.path.abspath(os.path.dirname(__file__))

urlparse.uses_netloc.append('redis')
redis_conf = dj_database_url.config('REDIS_URL')


class BaseConfig:

    """Base class all configuration inherits from."""

    DEBUG = True
    CACHE = NullCache()
    CACHE_TIMEOUT = 0
    SECRET_KEY = None


class DevelopmentConfig(BaseConfig):

    """Development specific configuration."""

    SECRET_KEY = 'my_secret_key'


class ProductionConfig(BaseConfig):

    """Production specific configuration."""

    DEBUG = False
    CACHE_TIMEOUT = 60 * 24 * 7
    CACHE = RedisCache(host=redis_conf.get('HOST'),
                       port=redis_conf.get('PORT'),
                       password=redis_conf.get('PASSWORD'))


class TestingConfig(BaseConfig):

    """Settings related to testing."""

    TESTING = True


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,

    'default': DevelopmentConfig
}
