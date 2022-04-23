import os


FLASK_RUN_FROM_CLI = os.environ.get('FLASK_RUN_FROM_CLI', '')

DATABASE_FILE = os.environ.get('DATABASE_FILE', 'app.sqlite')
SECRET_KEY = os.environ.get('SECRET_KEY', 'dev')

WS_LISTEN = os.environ.get('WS_LISTEN', '127.0.0.1')
WS_HOST = os.environ.get('WS_HOST', 'localhost')
WS_PORT = int(os.environ.get('WS_PORT', '8765'))

ONE_MINUTE = 60
CACHED_TIME = int(os.environ.get('CACHED_TIME', ONE_MINUTE * 15))
