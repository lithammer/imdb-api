# -*- coding: utf-8 -*-

import os
import re
import requests

from flask import Flask, Response, request, render_template, abort, jsonify
from bs4 import BeautifulSoup

from settings import HOST

PROJECT_ROOT = os.path.dirname(os.path.realpath(__file__))
app = Flask(__name__, static_folder=os.path.join(PROJECT_ROOT, 'static'),
        static_url_path='/static')


@app.errorhandler(404)
def page_not_found(error):
    return render_template('errors/404.html'), 404


@app.route('/')
def view_main():
    return render_template('index.html')


@app.route('/movie/poster/<file>')
def image(file):
    image = requests.get('http://ia.media-imdb.com/images/M/{}'.format(file))
    return Response(image.content, mimetype=image.headers['content-type'])


@app.route('/movie/<id>/')
def imdb(id):
    url = 'http://www.imdb.com/title/{}/'
    html = requests.get(url.format(id))

    if not html.ok:
        abort(404)

    try:
        soup = BeautifulSoup(html.text)
    except:
        return jsonify(error='couldn\'t parse')

    items = soup.find_all(itemprop=True)

    poster_width = int(request.args.get('w', '200'))
    poster_height = int(request.args.get('h', '296'))

    poster = soup.find(rel='image_src')['href']
    # Change poster size
    poster = re.sub(r'@@.+', '@@.SX{}_SY{}.jpg'.format(
        poster_width, poster_height), poster)
    poster = poster.rpartition('/')[2]
    poster = 'http://{}/movie/poster/{}'.format(HOST, poster)

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
            year=year,
            overview=description,
            vote_count=vote_count,
            vote_average=vote_average,
            genres=genres)

if __name__ == '__main__':
    if not 'HEROKU' in os.environ:
        app.debug = True
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port)
