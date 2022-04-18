import os
from urllib.parse import urlparse

from flask import Flask, render_template, request, redirect, send_from_directory

from utils.config import SECRET_KEY, DATABASE_FILE
from utils.db import init_app_db, get_db


app = Flask(__name__)
app.config.from_mapping(SECRET_KEY=SECRET_KEY, DATABASE=DATABASE_FILE)
init_app_db(app)

@app.route("/")
def start_page():
    db = get_db()

    jobs = []
    try:
        queue = get_default_queue(is_async=RQ_ASYNC_PROCESSING)

        for row in db.execute("SELECT created, game_id, name, job_id FROM jobs ORDER BY created DESC"):
            created, game_id, name, job_id = row

            try:
                job = Job.fetch(job_id, connection=queue.connection)

                jobs.append({"created": created, "game_id": game_id, "name": name, "job_id": job_id, "status": job.get_status(), "file": ""})
            except NoSuchJobError:
                filename = f'steam-scraper-master/{name}.csv'
                if os.path.exists(filename):
                    filename = f"{name}.csv"
                else:
                    filename = ""
                jobs.append({"created": created, "game_id": game_id, "name": name, "job_id": '', "status": "", "file": filename})

    except Exception as ex:
        pass 

    return render_template('index.html', jobs=jobs)
    