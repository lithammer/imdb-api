# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
import requests

from flask import Flask, Response, render_template, abort, jsonify
from bs4 import BeautifulSoup

from filters import support_jsonp, cached
from parser import IMDb

app = Flask(__name__)
app.config.from_object('settings')


@app.errorhandler(404)
def page_not_found(error):
    return render_template('errors/404.html'), 404


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/poster/<file>')
def proxy_image(file):
    """ Proxy the image since IMDb doesn't allow direct linking """
    image = requests.get('http://ia.media-imdb.com/images/M/{}'.format(file))
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
    except:
        abort(500)

    imdb = IMDb(soup, width, height)

    return jsonify(imdb.as_json())


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port)
