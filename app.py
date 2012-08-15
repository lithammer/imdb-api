import os
import requests
from flask import Flask, Response, render_template, abort, jsonify
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
        items = soup.find_all(itemprop=True)

        poster = 'http://{}/movie/poster/{}'.format(HOST,
                items[0]['src'].rpartition('/')[2])
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
    except:
        return 'Could not find!'

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port)
