#!/usr/bin/env python3

"""
mqtt.py

An ansible-rulebook event source plugin for receiving events via an mqtt topic.

Arguments:
    host:      The host where the mqtt topic is hosted
    topic:     The mqtt topic

Test script stand-alone by exporting MQTT_HOST and MQTT_TOPIC as environment variables
    - $ export MQTT_HOST=localhost
    - $ export MQTT_TOPIC=messages

In an EDA rulebook (note: fake collection, cloin.minecraft does not exist):

    - name: Minecraft events
      hosts: localhost
      sources:
        - cloin.minecraft.mqtt:
            host: localhost
            topic: messages

      rules:
        - name: New minecraft event
          condition: event.type is defined
          action:
            debug:

"""

import asyncio
import json
import logging
import os
from typing import Any, Dict

from aiomqtt import Client

async def main(queue: asyncio.Queue, args: Dict[str, Any]):
    logger = logging.getLogger()
    topic = args.get("topic")
    host = args.get("host")

    async with Client(host) as client:
        await client.subscribe(topic)
        async for message in client.messages:
            # Stupidly simple way of determining if response is JSON, which is
            # all we're interested in.
            if not message.payload.startswith(b'{'):
                continue

            payload = json.loads(message.payload)
            await queue.put({
                'topic': message.topic.value,
                'payload': json.loads(message.payload),
            })

if __name__ == "__main__":
    topic = os.environ.get('MQTT_TOPIC')
    host = os.environ.get('MQTT_HOST')

    class MockQueue:
        print(f"Waiting for messages on '{topic}'...")
        async def put(self, event):
            print(event)

    asyncio.run(main(MockQueue(), {"topic": topic, "host": host}))
