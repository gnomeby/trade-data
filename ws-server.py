#!/usr/bin/env python

import asyncio
import json
import uuid
import websockets
from collections import defaultdict
from datetime import datetime, timezone

from utils.config import SECRET_KEY, WS_LISTEN, WS_PORT, CACHED_TIME


CONNECTIONS = set()
SUBSCRIPTIONS = defaultdict(set)
PUBLISHERS = {}
CACHED_STREAMS = defaultdict(list)

async def do(websocket):
    print("New connection:", websocket)
    CONNECTIONS.add(websocket)

    async for message in websocket:
        response = {"msg": "OK"}

        try:
            data = json.loads(message)
            command = data["cmd"]
            topic = data.get("topic")

            if "subscribe" == command:
                SUBSCRIPTIONS[topic].add(websocket)
                response["subscribed"] = topic
                print("Subscribed to %s:" % topic, websocket)
                await websocket.send(json.dumps(response))

                after = int(data.get("after", "0")) // 1000
                if after:
                    for (cur_date, cur_delta) in CACHED_STREAMS[topic]:
                        if cur_date > after:
                            await websocket.send(json.dumps(
                                {"date": cur_date * 1000, "delta": cur_delta}
                            ))

            elif "unsubscribe" == command:
                SUBSCRIPTIONS[topic].remove(websocket)
                response["unsubscribed"] = topic

                print("Unsubscribed from %s:" % topic, websocket)
                await websocket.send(json.dumps(response))

            elif "unsubscribe_all" == command:
                for cur_topic in SUBSCRIPTIONS.keys():
                    if websocket in SUBSCRIPTIONS[cur_topic]:
                        SUBSCRIPTIONS[cur_topic].remove(websocket)

                print("Unsubscribed from all", websocket)
                await websocket.send(json.dumps(response))

            elif "publisher" == command:
                if data["secret_key"] != SECRET_KEY:
                    await websocket.send('{"error": "incorrect secret_key"}')

                elif websocket in PUBLISHERS.values():
                    await websocket.send('{"error": "already approved"}')

                else:
                    user_id = uuid.uuid4().hex
                    PUBLISHERS[user_id] = websocket

                    print("Added to publishers:", websocket)
                    response["user_id"] = user_id
                    await websocket.send(json.dumps(response))

            elif "inbox" == command:
                if data["user_id"] not in PUBLISHERS:
                    await websocket.send('{"error": "unknown publisher"}')
                else:
                    websockets.broadcast(SUBSCRIPTIONS[topic], json.dumps(
                        {"date": data["date"] * 1000, "delta": data["delta"]}
                    ))

                    CACHED_STREAMS[topic].append((data["date"], data["delta"]))

                    # Clear old cache
                    current_ts = datetime.now(timezone.utc).timestamp()
                    if CACHED_STREAMS[topic] and (CACHED_STREAMS[topic][0][0] + CACHED_TIME * 3) < current_ts:
                        for index in range(len(CACHED_STREAMS[topic])):
                            if (CACHED_STREAMS[topic][0][0] + CACHED_TIME * 2) > current_ts:
                                CACHED_STREAMS[topic] = CACHED_STREAMS[topic][index:]
                                break

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
