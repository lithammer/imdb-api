from functools import wraps
import os
import requests

from flask import (Flask, Response, request, render_template, abort, jsonify,
                   current_app)
from bs4 import BeautifulSoup

from settings import config
from parser import IMDb

app = Flask(__name__)
app.config.from_object(config[os.getenv('FLASK_SETTINGS', 'default')])


def support_jsonp(f):
    """Wraps JSONified output for JSONP."""
    @wraps(f)
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
    @wraps(f)
    def decorated_function(*args, **kwargs):
        cache = app.config['CACHE']
        response = cache.get(request.path)
        ttl = timeout or app.config['CACHE_TIMEOUT']
        if response is None:
            response = f(*args, **kwargs)
            cache.set(request.path, response, ttl)
        return response
    return decorated_function


@app.errorhandler(404)
def page_not_found(error):
    return render_template('errors/404.html'), 404


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/poster/<filename>')
def proxy_image(filename):
    """Proxy the image since IMDb doesn't allow direct linking."""
    image = requests.get('http://ia.media-imdb.com/images/M/%s' % filename)
    return Response(image.content, mimetype=image.headers['content-type'])


@app.route('/<id>/<int:width>/<int:height>')
@app.route('/<id>/<int:width>')
@app.route('/<id>')
@support_jsonp
@cached
def get(id, width=200, height=296):
    html = requests.get('http://m.imdb.com/title/{}/'.format(id))

    if not html.ok:
        abort(404)

    try:
        soup = BeautifulSoup(html.text, 'lxml')
    except Exception:
        abort(500)

    imdb = IMDb(soup, width, height)

    return jsonify(imdb.as_json())


if __name__ == '__main__':
    app.run(host='0.0.0.0')
