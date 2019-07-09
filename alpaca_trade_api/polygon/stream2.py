import asyncio
import json
import re
import os
import websockets
from .entity import (
    Quote, Trade, Agg, Entity,
)


class StreamConn(object):
    def __init__(self, key_id=None):
        self._key_id = key_id
        self._endpoint = os.environ.get(
            'POLYGON_WS_URL',
            'wss://alpaca.socket.polygon.io/stocks'
        ).rstrip('/')
        self._handlers = {}
        self._ws = None

    async def connect(self):
        print('connecting to polygon')
        ws = await websockets.connect(self._endpoint)
        await ws.send(json.dumps({
            'action': 'auth',
            'params': self._key_id
        }))
        r = await ws.recv()
        if isinstance(r, bytes):
            r = r.decode('utf-8')
        msg = json.loads(r)
        if msg[0].get('status') != 'connected':
            raise ValueError(
                ("Invalid Polygon credentials, Failed to authenticate: {}"
                    .format(msg))
            )

        self._ws = ws
        await self._dispatch('authorized', msg[0])

        asyncio.ensure_future(self._consume_msg())
        return ws

    async def _consume_msg(self):
        ws = self._ws
        try:
            while True:
                r = await ws.recv()
                if isinstance(r, bytes):
                    r = r.decode('utf-8')
                msg = json.loads(r)
                for update in msg:
                    stream = update.get('ev')
                    if stream is not None:
                        await self._dispatch(stream, update)
        finally:
            await ws.close()
            self._ws = None

    async def _ensure_ws(self):
        if self._ws is not None:
            return
        self._ws = await self.connect()

    async def subscribe(self, channels):
        '''Start subscribing channels.
        If the necessary connection isn't open yet, it opens now.
        '''
        if len(channels) > 0:
            await self._ensure_ws()
            # Join channel list to string
            streams = ','.join(channels)
            await self._ws.send(json.dumps({
                'action': 'subscribe',
                'params': streams
            }))

    def run(self, initial_channels=[]):
        '''Run forever and block until exception is rasised.
        initial_channels is the channels to start with.
        '''
        loop = asyncio.get_event_loop()
        try:
            loop.run_until_complete(self.subscribe(initial_channels))
            loop.run_forever()
        finally:
            loop.run_until_complete(self.close())

    async def close(self):
        '''Close any of open connections'''
        if self._ws is not None:
            await self._ws.close()

    def _cast(self, subject, data):
        if subject == 'T':
            map = {
                "sym": "symbol",
                "c": "conditions",
                "x": "exchange",
                "p": "price",
                "s": "size",
                "t": "timestamp"
            }
            ent = Trade({map[k]: v for k, v in data.items() if k in map})
        elif subject == 'Q':
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
        elif subject == 'AM' or subject == 'A':
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
                "vw": "vwap",
                "av": "totalvolume",
                "op": "dailyopen",    # depricated? stream often has 0 for op
            }
            ent = Agg({map[k]: v for k, v in data.items() if k in map})
        else:
            ent = Entity(data)
        return ent

    async def _dispatch(self, channel, msg):
        for pat, handler in self._handlers.items():
            if pat.match(channel):
                ent = self._cast(channel, msg)
                await handler(self, channel, ent)

    def on(self, channel_pat):
        def decorator(func):
            self.register(channel_pat, func)
            return func

        return decorator

    def register(self, channel_pat, func):
        if not asyncio.iscoroutinefunction(func):
            raise ValueError('handler must be a coroutine function')
        if isinstance(channel_pat, str):
            channel_pat = re.compile(channel_pat)
        self._handlers[channel_pat] = func

    def deregister(self, channel_pat):
        if isinstance(channel_pat, str):
            channel_pat = re.compile(channel_pat)
        del self._handlers[channel_pat]
