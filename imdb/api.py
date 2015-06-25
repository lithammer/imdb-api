from bs4 import BeautifulSoup
from flask import Response, render_template, abort, jsonify
import requests

from imdb import app
from imdb.decorators import cached, support_jsonp
from imdb.parser import IMDb


@app.errorhandler(404)
def page_not_found(error):
    return render_template('errors/404.html'), 404


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/poster/<filename>')
@cached
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
    html = requests.get('http://m.imdb.com/title/%s/' % id)

    if not html.ok:
        abort(404)

    try:
        soup = BeautifulSoup(html.text, 'lxml')
    except Exception:
        abort(500)

    imdb = IMDb(soup, width, height)

    return jsonify(imdb.as_json())
