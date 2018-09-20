import asyncio
import re
from nats.aio.client import Client as NATS

from .entity import (
    Quote, Trade, Agg, Entity,
)

import json


class Stream(object):

    def __init__(self, api_key):
        self._api_key = api_key
        self._nc = NATS()
        self._handlers = {}
        self._ssids = []

    async def connect(self, loop=None):
        servers = [
            'nats://{}@nats1.polygon.io:31101'.format(self._api_key),
            'nats://{}@nats2.polygon.io:31102'.format(self._api_key),
            'nats://{}@nats3.polygon.io:31103'.format(self._api_key),
        ]

        # TODO:
        async def error_callback(exc):
            import traceback
            traceback.print_exc()

        await self._nc.connect(
            servers=servers,
            io_loop=loop,
            error_cb=error_callback,
        )

    async def subscribe(self, topics):
        for ssid in self._ssids:
            await self._nc.unsubscribe(ssid)
        ssids = []
        for topic in topics:
            ssid = await self._nc.subscribe(topic, cb=self._dispatch)
            ssids.append(ssid)
        self._ssids = ssids

    async def close(self):
        await self._nc.close()

    def _cast(self, subject, data):
        if subject.startswith('T.'):
            map = {
                "sym": "symbol",
                "c": "conditions",
                "x": "exchange",
                "p": "price",
                "s": "size",
                "t": "timestamp"
            }
            ent = Trade({map[k]: v for k, v in data.items() if k in map})
        elif subject.startswith('Q.'):
            map = {
                "sym": "symbol",
                "ax": "askexchange",
                "ap": "askprice",
                "as": "asksize",
                "bx": "bidexchange",
                "bp": "bidprice",
                "bs": "bidsize",
                "c": "condition",
                "t": "timestamp"
            }
            ent = Quote({map[k]: v for k, v in data.items() if k in map})
        elif subject.startswith('AM.'):
            map = {
                "sym": "symbol",
                "a": "average",
                "c": "close",
                "h": "high",
                "k": "transactions",
                "l": "low",
                "o": "open",
                "t": "totalvalue",
                "x": "exchange",
                "v": "volume",
                "s": "start",
                "e": "end",
            }
            ent = Agg({map[k]: v for k, v in data.items() if k in map})
        else:
            ent = Entity(data)
        return ent

    async def _dispatch(self, msg):
        subject = msg.subject
        data = json.loads(msg.data.decode())

        for pat, handler in self._handlers.items():
            if pat.match(subject):
                ent = self._cast(subject, data)
                await handler(self, subject, ent)

    def on(self, subject_pat):
        def decorator(func):
            self.register(subject_pat, func)
            return func
        return decorator

    def register(self, subject_pat, func):
        if not asyncio.iscoroutinefunction(func):
            raise ValueError('func must be a coroutine function')
        if isinstance(subject_pat, str):
            subject_pat = re.compile(subject_pat)
        self._handlers[subject_pat] = func

    def deregister(self, subject_pat):
        if isinstance(subject_pat, str):
            subject_pat = re.compile(subject_pat)
        del self._handlers[subject_pat]
