import os

from werkzeug.contrib.cache import RedisCache, NullCache


class BaseConfig(object):

    DEBUG = True
    CACHE = NullCache()
    CACHE_TIMEOUT = 0
    SECRET_KEY = None


class DevelopmentConfig(BaseConfig):

    SECRET_KEY = 'my_secret_key'


class ProductionConfig(BaseConfig):

    DEBUG = False
    CACHE_TIMEOUT = 60 * 24 * 7
    CACHE = RedisCache(host=os.environ.get('REDIS_HOST'),
                       port=os.environ.get('REDIS_PORT'),
                       password=os.environ.get('REDIS_PASSWORD'))


class TestingConfig(BaseConfig):

    TESTING = True

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,

    'default': DevelopmentConfig
}
