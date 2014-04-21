from datetime import datetime
import os
import re

from flask import request


class IMDb:

    def __init__(self, html, width, height):
        self.html = html
        self.width = width
        self.height = height

    @property
    def poster(self):
        poster = self.html.find_all('img')[1].attrs['src']
        poster = re.sub(r'@@.+', '@@.SX{width}_SY{height}.jpg'.format(
            width=self.width, height=self.height), poster)
        poster = poster.rpartition('/')[2]
        host = os.getenv('HOSTNAME', default=request.headers['Host'])
        poster = 'http://{}/poster/{}'.format(host, poster)

        # Unreleased movies use this for placeholder
        if poster.rpartition('/')[2] == 'film-81x120.png':
            poster = ''
        return poster

    @property
    def title(self):
        title = re.match(r'[\w\s]+\w', self.html.title.string).group(0)
        return title

    @property
    def vote_count(self):
        try:
            node = self.html.find('span', {'class': 'inline-block'})
            vote_count = node.contents[1].contents[-1]
            vote_count = int(vote_count.replace(',', ''))
        except IndexError:
            vote_count = 0
        return vote_count

    @property
    def vote_average(self):
        try:
            vote_average = self.html.find('span', {'class':
                'inline-block'})
            vote_average = float(vote_average.contents[0])
        except AttributeError:
            vote_average = 0
        return vote_average

    @property
    def plot_summary(self):
        text = self.html.find('p', {'itemprop': 'description'}).text
        return text.strip()

    @property
    def release_date(self):
        release_date = ''
        for e in self.html.find_all('h3', {'class': 'inline-block'}):
            if e.text == 'Release Date:':
                release_date = e.find_next_sibling('span').text
                release_date = datetime.strptime(release_date, '%d %B %Y')
                release_date = '{:%Y-%m-%d}'.format(release_date)
        return release_date

    @property
    def run_time(self):
        node = self.html.find('time', {'itemprop': 'duration'})
        return node.text.strip()

    @property
    def genres(self):
        genres = []
        for node in self.html.find_all('span', {'itemprop': 'genre'}):
            genres.append(node.text)
        return genres

    def as_json(self):
        return {
            'poster': self.poster,
            'title': self.title,
            'release_date': self.release_date,
            'plot_summary': self.plot_summary,
            'vote_count': self.vote_count,
            'vote_average': self.vote_average,
            'run_time': self.run_time,
            'genres': self.genres
        }
