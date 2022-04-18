from email.policy import default
from random import random
from time import sleep
from datetime import datetime

import click
from flask.cli import with_appcontext

from utils.db import get_db, close_db


def generate_movement():
    movement = -1 if random() < 0.5 else 1
    return movement

@click.command('data-generator')
@click.argument('amount', default=100) #, help='amount of tickers')
@click.argument('interval', default=1) #, help='interval in seconds')
@with_appcontext
def data_generator(amount=100, interval=1):
    """Generate test data for DB."""

    db = get_db()
    click.echo('Starting data generator.')

    while(True):
        for i in range(amount):
            name = "ticker_%02d" % i
            db.execute(
                "INSERT INTO prices (name, price_cents) VALUES (?, ?)", (name, generate_movement() * 100),
            )
        db.commit()
        click.echo('Generated %d ticker prices, %s' % (amount, datetime.now().isoformat()))

        sleep(1.0)

def init_data_cli(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(data_generator)
