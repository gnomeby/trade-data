import time

from flask import Flask, render_template, request, send_from_directory, jsonify, Response

from utils.config import SECRET_KEY, DATABASE_FILE, FLASK_RUN_FROM_CLI, WS_HOST, WS_PORT
from utils.data import init_data_cli
from utils.db import init_db_cli, get_db

ONE_HOUR = 3600
ONE_MINUTE = 60


app = Flask(__name__, static_folder=FLASK_RUN_FROM_CLI and "static" or None, static_url_path='/static')
app.config.from_mapping(SECRET_KEY=SECRET_KEY, DATABASE=DATABASE_FILE)
init_db_cli(app)
init_data_cli(app)

@app.route("/favicon.ico")
def favicon():
    return send_from_directory('static', 'favicon.ico')

@app.route("/")
def start_page():
    db = get_db()

    names = []
    try:
        for row in db.execute("SELECT DISTINCT name FROM prices ORDER BY name ASC"):
            (name,) = row

            names.append(name)
    except Exception as ex:
        print(ex)
        pass

    return render_template('index.html', names=names, WS_HOST=WS_HOST, WS_PORT=WS_PORT)

@app.route("/initial_data")
def initial_data():
    topic = request.args.get("topic")
    period = request.args.get("period")
    assert 'ticker' in topic
    assert period == 'last'

    db = get_db()

    data = []
    for row in db.execute("SELECT created, price_cents FROM prices WHERE name = ? ORDER BY created ASC", (topic, )):
        (created, price_cents) = row
        data.append([time.mktime(created.timetuple()), price_cents / 100])

    result = jsonify(data)
    result.headers['Cache-Control'] = 'public, smax-age=%d, max-age=%d,' % (ONE_HOUR // 4, ONE_HOUR // 4 - ONE_MINUTE)

    return result
