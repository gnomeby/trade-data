import os
from urllib.parse import urlparse


FLASK_RUN_FROM_CLI = os.environ.get('FLASK_RUN_FROM_CLI', '')

DATABASE_FILE = os.environ.get('DATABASE_FILE', 'app.sqlite')
SECRET_KEY = os.environ.get('SECRET_KEY', 'dev')
