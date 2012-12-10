# -*- coding: utf-8 -*-

import datetime
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
    """ Fetches and scrapes a movie by imdb id """
    html = requests.get('http://m.imdb.com/title/{}/'.format(id))
    host = request.headers['Host']

    if not html.ok:
        abort(404)

    try:
        soup = BeautifulSoup(html.text, 'lxml')
    except:
        return jsonify(error='Error occured while parsing.')

    poster = soup.find_all('img')[1].attrs['src']
    poster = re.sub(r'@@.+', '@@.SX{width}_SY{height}.jpg'.format(
        width=width, height=height), poster)
    poster = poster.rpartition('/')[2]
    poster = 'http://{}/poster/{}'.format(host, poster)

    title = re.match(r'[\w\s]+\w', soup.title.string).group(0)
    vote_average = float(soup.strong.string)

    vote_count = soup.find_all('p', {'class': 'votes'})[0].contents[2]
    vote_count = re.search(r'\(([\d,]+)', vote_count)
    vote_count = int(vote_count.groups()[0].replace(',', ''))

    details = soup.find('section', {'class': 'details'}).find_all('p')

    release_date = datetime.datetime.strptime(details[0].string, ' %d %b %Y')
    release_date = '{:%Y-%m-%d}'.format(release_date)

    genres = details[1].string.split(', ')
    run_time = details[2].string
    description = details[4].contents[0].strip()

    return jsonify(poster=poster,
                   title=title,
                   release_date=release_date,
                   overview=description,
                   vote_count=vote_count,
                   vote_average=vote_average,
                   run_time=run_time,
                   genres=genres)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port)
