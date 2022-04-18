import os
from urllib.parse import urlparse

from flask import Flask, render_template, request, redirect, send_from_directory

from utils.config import SECRET_KEY, DATABASE_FILE
from utils.data import init_data_cli
from utils.db import init_db_cli, get_db


app = Flask(__name__)
app.config.from_mapping(SECRET_KEY=SECRET_KEY, DATABASE=DATABASE_FILE)
init_db_cli(app)
init_data_cli(app)

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

    return render_template('index.html', names=names)
