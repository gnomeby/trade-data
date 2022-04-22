#!/usr/bin/env python

import asyncio
from collections import defaultdict
import json
import uuid
import websockets

from utils.config import SECRET_KEY, WS_HOST, WS_LISTEN, WS_PORT


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
            topic = data.get("topic")

            if "subscribe" == data["cmd"]:
                SUBSCRIPTIONS[topic].add(websocket)
                response["subscribed"] = topic
                print("Subscribed to %s:" % topic, websocket)

            elif "unsubscribe" == data["cmd"]:
                SUBSCRIPTIONS[topic].remove(websocket)
                response["unsubscribed"] = topic
                print("Unsubscribed from %s:" % topic, websocket)

            elif "unsubscribe_all" == data["cmd"]:
                for cur_topic in SUBSCRIPTIONS.keys():
                    if websocket in SUBSCRIPTIONS[cur_topic]:
                        SUBSCRIPTIONS[cur_topic].remove(websocket)
                print("Unsubscribed from all", websocket)

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
                    print("Added to publishers:", websocket)
                    response["user_id"] = user_id

            elif "inbox" == data["cmd"]:
                if data["user_id"] not in PUBLISHERS:
                    await websocket.send('{"error": "unknown publisher"}')
                else:
                    websockets.broadcast(SUBSCRIPTIONS[topic], json.dumps(
                        {"date": data["date"], "delta": data["delta"]}
                    ))

            await websocket.send(json.dumps(response))
        except AlreadyProcessed:
            pass
        except Exception as ex:
            await websocket.send('{"error": "bad request", "details": "%s"}' % ex.args[0])

    for user_id in list(PUBLISHERS.keys()):
        if PUBLISHERS[user_id] == websocket:
            del PUBLISHERS[user_id]
            print("Removed from publishers:", websocket)

    for topic, items in SUBSCRIPTIONS.items():
        if websocket in items:
            SUBSCRIPTIONS[topic].remove(websocket)
            print("Unsubscribed from %s:" % topic, websocket)

    CONNECTIONS.remove(websocket)
    print("Closed connection:", websocket)

async def main():
    async with websockets.serve(do, WS_LISTEN, WS_PORT):
        print("Starting WesSocker server at %s:%s" % (WS_LISTEN, WS_PORT))
        await asyncio.Future()  # run forever

asyncio.run(main())
