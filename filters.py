# -*- coding: utf-8 -*-

from functools import wraps

from flask import request, current_app

from settings import CACHE_TIMEOUT, CACHE

cache = CACHE


def support_jsonp(f):
    """ Wraps JSONified output for JSONP """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        response = f(*args, **kwargs)
        callback = request.args.get('callback', False)
        if callback:
            content = '%s(%s)' % (callback, response.data)
            response = current_app.response_class(
                content, mimetype='application/javascript')
        return response
    return decorated_function


def cached(f, timeout=None):
    """ Simple URL based cache """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        response = cache.get(request.path)
        if response is None:
            response = f(*args, **kwargs)
            cache.set(request.path, response, timeout or CACHE_TIMEOUT)
        return response
    return decorated_function
