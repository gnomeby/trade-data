import asyncio
import json
import random
from datetime import datetime, timezone

import click
import websockets

from flask.cli import with_appcontext

from utils.config import SECRET_KEY, WS_HOST, WS_PORT
from utils.db import get_db, close_db


def generate_movement():
    return random.choice([-1, 1])

async def publisher(amount: int, interval: float):
    # Connecting
    db = get_db()
    async with websockets.connect(f"ws://{WS_HOST}:{WS_PORT}") as websocket:
        await websocket.send(json.dumps({"cmd": "publisher", "secret_key": SECRET_KEY}))
        response = json.loads(await websocket.recv())
        user_id = response["user_id"]

        # Publishing
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
            click.echo('Generated %d ticker prices, %s' % (amount, datetime.now(timezone.utc).isoformat()))

            for name, delta in prices_delta_map.items():
                await websocket.send(json.dumps(
                    {
                        "cmd": "inbox", "user_id": user_id,
                        "topic": name, "date": int(datetime.now(timezone.utc).timestamp()), "delta": delta,
                    }
                ))

            await asyncio.sleep(interval)

@click.command('data-generator')
@click.argument('amount', default=100) #, help='amount of tickers')
@click.argument('interval', default=1.0) #, help='interval in seconds')
@with_appcontext
def data_generator(amount=100, interval=1.0):
    """Generate test data for DB."""

    click.echo('Starting data generator.')
    asyncio.run(publisher(amount, interval))


def init_data_cli(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(data_generator)
