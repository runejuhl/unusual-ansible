#!/usr/bin/env python3

"""
http_sse.py

FIXME: You should write something here, Rune.

"""

import asyncio
import json
import logging
import os
from typing import Any, Dict

import aiohttp
from aiosseclient import aiosseclient

async def main(queue: asyncio.Queue, args: Dict[str, Any]):
  logger = logging.getLogger()
  url = args.get('url')
  event_ids = args.get('event_ids', None)

  async for event in aiosseclient(url):
    if event.event in ['log', 'ping']:
      continue

    # print(type(event), event.event, event.id, event.data, event.data[0] == r'{')

    if not event.data[0] == r'{':
      continue

    data = json.loads(event.data)
    if event_ids:
      if not data['id'] in event_ids:
        continue

    await queue.put({
      'event': event.event,
      'id':    event.id,
      'data':  data,
    })

if __name__ == "__main__":
  url = os.environ.get('SSE_HOST')

  class MockQueue:
    print('Waiting for events...')
    async def put(self, event):
      print(event)

  asyncio.run(main(MockQueue(),
                   '{"id":"number-zout1_y-end","name":"Zout1 Y-End","min_value":0,"max_value":7500,"step":10,"mode":1,"value":0,"state":"0 mm"}'))
