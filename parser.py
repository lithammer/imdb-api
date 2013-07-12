# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import datetime
import os
import re

from flask import request


class IMDb:

    def __init__(self, html, width, height):
        self.html = html
        self.width = width
        self.height = height

    _details = None

    def _get_detail(self, key):
        details = self._details if self._details else self.html.find_all('h1')
        self._details = details
        detail = [x for x in details if x.text == key]
        if detail:
            return detail[0].find_next().contents[0].strip()
        return ''

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
            vote_count = self.html.find_all('p', {'class': 'votes'})[0].contents[2]
            vote_count = re.search(r'\(([\d,]+)', vote_count)
            vote_count = int(vote_count.groups()[0].replace(',', ''))
        except IndexError:
            vote_count = 0
        return vote_count

    @property
    def vote_average(self):
        try:
            vote_average = float(self.html.strong.string)
        except AttributeError:
            vote_average = 0
        return vote_average

    @property
    def plot_summary(self):
        return self._get_detail('Plot Summary')

    @property
    def release_date(self):
        release_date = self._get_detail('Release Date')
        release_date = datetime.datetime.strptime(release_date, '%d %b %Y')
        release_date = '{:%Y-%m-%d}'.format(release_date)
        return release_date

    @property
    def run_time(self):
        return self._get_detail('Run time')

    @property
    def genres(self):
        return self._get_detail('Genre').split(', ')

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
