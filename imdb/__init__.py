import os

from flask import Flask

from imdb.config import config

app = Flask(__name__)
app.config.from_object(config[os.environ.get('FLASK_SETTINGS', 'default')])

import imdb.api  # noqa
