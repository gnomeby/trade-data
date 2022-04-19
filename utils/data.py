import json
import random
from time import sleep, time
from datetime import datetime
import websockets

import click
from flask.cli import with_appcontext

from utils.config import SECRET_KEY
from utils.db import get_db, close_db


def generate_movement():
    return random.choice([-1, 1])


@click.command('data-generator')
@click.argument('amount', default=100) #, help='amount of tickers')
@click.argument('interval', default=1) #, help='interval in seconds')
@with_appcontext
def data_generator(amount=100, interval=1):
    """Generate test data for DB."""

    db = get_db()
    click.echo('Starting data generator.')

    with websockets.connect("ws://localhost:8765") as websocket:
        websocket.send(json.dumps({"cmd": "publisher", "secret_key": SECRET_KEY}))
        response = json.loads(websocket.recv())
        user_id = response["user_id"]

        while(True):
            prices_delta_map = {}
            for i in range(amount):
                name = "ticker_%02d" % i
                delta = generate_movement() * 100
                prices_delta_map[name] = delta
                db.execute(
                    "INSERT INTO prices (name, price_cents) VALUES (?, ?)", (name, delta),
                )
            db.commit()
            click.echo('Generated %d ticker prices, %s' % (amount, datetime.now().isoformat()))

            for name, delta in prices_delta_map.items():
                websocket.send(json.dumps(
                    {
                        "user_id": user_id,
                        "topic": name, "date": int(time()), "delta": delta,
                    }
                ))

            sleep(1.0)

def init_data_cli(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(data_generator)
