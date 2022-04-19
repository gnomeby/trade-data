#!/usr/bin/env python

import asyncio
from collections import defaultdict
import json
import uuid
import websockets

from utils.config import SECRET_KEY


CONNECTIONS = set()
SUBSCRIPTIONS = defaultdict(set)
PUBLISHERS = {}

class AlreadyProcessed(Exception):
    pass

async def do(websocket):
    print("New connection:", websocket)
    CONNECTIONS.add(websocket)

    async for message in websocket:
        response = {"msg": "OK"}

        try:
            data = json.loads(message)

            if "subscribe" == data["cmd"]:
                SUBSCRIPTIONS[data["topic"]].add(websocket)

            elif "unsubscribe" == data["cmd"]:
                SUBSCRIPTIONS[data["topic"]].remove(websocket)

            elif "publisher" == data["cmd"]:
                if data["secret_key"] != SECRET_KEY:
                    await websocket.send('{"error": "incorrect secret_key"}')
                    raise AlreadyProcessed()

                elif websocket in PUBLISHERS.values():
                    await websocket.send('{"error": "already approved"}')
                    raise AlreadyProcessed()
                else:
                    user_id = uuid.uuid4().hex
                    PUBLISHERS[user_id] = websocket
                    response["user_id"] = user_id

            elif "news" == data["cmd"]:
                if data["user_id"] not in PUBLISHERS:
                    await websocket.send('{"error": "unknown publisher"}')
                else:
                    websockets.broadcast(SUBSCRIPTIONS[data["topic"]], json.dumps(
                        {"date": data["date"], "delta": data["delta"]}
                    ))

            await websocket.send(json.dumps(response))
        except AlreadyProcessed:
            pass
        except Exception as ex:
            await websocket.send('{"error": "bad request", "details": "%s"}' % ex.args[0])


async def main():
    async with websockets.serve(do, "localhost", 8765):
        await asyncio.Future()  # run forever

asyncio.run(main())
