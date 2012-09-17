# -*- coding: utf-8 -*-

import os
import re
import requests

from flask import Flask, Response, request, render_template, abort, jsonify
from bs4 import BeautifulSoup

from filters import support_jsonp, cached

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


@app.route('/search/<id>/<int:width>/<int:height>')
@app.route('/search/<id>/<int:width>')
@app.route('/search/<id>')
@support_jsonp
@cached
def search(id, width=200, height=296):
    """ Fetches and scrapes a movie or tv show by imdb id """
    html = requests.get('http://www.imdb.com/title/{}/'.format(id))
    host = request.headers['Host']

    if not html.ok:
        abort(404)

    try:
        soup = BeautifulSoup(html.text, 'lxml')
    except:
        return jsonify(error='Error occured while parsing.')

    items = soup.find_all(itemprop=True)

    poster = soup.find(rel='image_src')['href']
    # Change poster size
    poster = re.sub(r'@@.+', '@@.SX{}_SY{}.jpg'.format(
        width, height), poster)
    poster = poster.rpartition('/')[2]
    poster = 'http://{}/movie/poster/{}'.format(host, poster)

    title = list(items[1].strings)[0].strip()
    description = items[8].text.strip()
    vote_count = int(items[5].text.replace(',', ''))
    vote_average = float(items[3].text)

    year = soup.time['datetime']

    genres = []
    for g in soup.find_all(itemprop='genre'):
        genres.append(g.strings.next())

    return jsonify(poster=poster,
            title=title,
            release_date=year,
            overview=description,
            vote_count=vote_count,
            vote_average=vote_average,
            genres=genres)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port)
