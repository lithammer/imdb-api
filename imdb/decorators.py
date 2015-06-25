import functools

from flask import request, current_app

from imdb import app


def support_jsonp(f):
    """Wraps JSONified output for JSONP."""
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        response = f(*args, **kwargs)
        callback = request.args.get('callback')
        if callback is not None:
            content = '%s(%s)' % (callback, response.data)
            response = current_app.response_class(
                content, mimetype='application/javascript')
        return response
    return decorated_function


def cached(f, timeout=None):
    """Simple URL based cache."""
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        cache = app.config['CACHE']
        response = cache.get(request.path)
        ttl = timeout or app.config['CACHE_TIMEOUT']
        if response is None:
            response = f(*args, **kwargs)
            cache.set(request.path, response, ttl)
        return response
    return decorated_function
