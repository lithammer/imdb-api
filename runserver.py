import sys

from waitress import serve

from app import app

try:
    port = sys.argv[1]
except IndexError:
    port = 8080

serve(app, port=port)
