# -*- coding: utf-8 -*-

import os

HOST = 'imdb-api.herokuapp.com'
DEBUG = False

# Dev settings
if not os.environ.get('HEROKU'):
    HOST = 'localhost'
    DEBUG = True
