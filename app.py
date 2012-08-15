import os
from flask import Flask, Response, render_template, abort, jsonify
from bs4 import BeautifulSoup
import requests

PROJECT_ROOT = os.path.dirname(os.path.realpath(__file__))
app = Flask(__name__, static_folder=os.path.join(PROJECT_ROOT, 'static'), static_url_path='/static')


@app.errorhandler(404)
def page_not_found(error):
    return render_template('errors/404.html'), 404


@app.route('/')
def view_main():
    return render_template('index.html')


@app.route('/imdb/poster/<id>/')
def image(id):
    image = requests.get('http://ia.media-imdb.com/images/M/{}'.format(id))
    return Response(image.content, mimetype=image.headers['content-type'])


@app.route('/imdb/<id>/')
def imdb(id):
    url = 'http://www.imdb.com/title/{}/'
    html = requests.get(url.format(id))

    if not html.ok:
        abort(404)
    try:
        soup = BeautifulSoup(html.text)
        items = soup.find_all(itemprop=True)
        poster = items[0]['src'].rpartition('/')[2]
        title = list(items[1].strings)[0].strip()
        if list(items[1].strings)[1] == '(':
            year = list(items[1].strings)[2].strip()
        else:
            year = list(items[1].strings)[4].strip()
        description = items[8].text.strip()
        vote_count = int(items[5].text.replace(',', ''))
        vote_average = float(items[3].text)
        return jsonify(poster=poster,
                title=title,
                year=year,
                overview=description,
                vote_count=vote_count,
                vote_average=vote_average)
    except:
        return 'Could not find!'

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port)
