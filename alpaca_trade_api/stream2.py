import asyncio
import json
import os
import re
import websockets
from .common import get_base_url, get_credentials
from .entity import Account, Entity
from . import polygon
import logging


class StreamConn(object):
    def __init__(self, key_id=None, secret_key=None, base_url=None):
        self._key_id, self._secret_key, _ = get_credentials(key_id, secret_key)
        base_url = re.sub(r'^http', 'ws', base_url or get_base_url())
        self._endpoint = base_url + '/stream'
        self._handlers = {}
        self._handler_symbols = {}
        self._base_url = base_url
        self._streams = set([])
        self._ws = None
        self._retry = int(os.environ.get('APCA_RETRY_MAX', 3))
        self._retry_wait = int(os.environ.get('APCA_RETRY_WAIT', 3))
        self._retries = 0
        self.polygon = None
        try:
            self.loop = asyncio.get_event_loop()
        except websockets.WebSocketException as wse:
            logging.warn(wse)
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)

    async def _connect(self):
        ws = await websockets.connect(self._endpoint)
        await ws.send(json.dumps({
            'action': 'authenticate',
            'data': {
                'key_id': self._key_id,
                'secret_key': self._secret_key,
            }
        }))
        r = await ws.recv()
        if isinstance(r, bytes):
            r = r.decode('utf-8')
        msg = json.loads(r)

        if 'data' not in msg or msg['data']['status'] != 'authorized':
            raise ValueError(
                ("Invalid Alpaca API credentials, Failed to authenticate: {}"
                    .format(msg))
            )
        else:
            self._retries = 0

        self._ws = ws
        await self._dispatch('authorized', msg)

        asyncio.ensure_future(self._consume_msg())

    async def _consume_msg(self):
        ws = self._ws
        try:
            while True:
                r = await ws.recv()
                if isinstance(r, bytes):
                    r = r.decode('utf-8')
                msg = json.loads(r)
                stream = msg.get('stream')
                if stream is not None:
                    await self._dispatch(stream, msg)
        except websockets.WebSocketException as wse:
            logging.warn(wse)
            await self.close()
            asyncio.ensure_future(self._ensure_ws())

    async def _ensure_polygon(self):
        if self.polygon is not None:
            return
        key_id = self._key_id
        if 'staging' in self._base_url:
            key_id += '-staging'
        self.polygon = polygon.StreamConn(key_id)
        self.polygon._handlers = self._handlers.copy()
        self.polygon._handler_symbols = self._handler_symbols.copy()
        await self.polygon.connect()

    async def _ensure_ws(self):
        if self._ws is not None:
            return

        while self._retries <= self._retry:
            try:
                await self._connect()
                if self._streams:
                    await self.subscribe(self._streams)
                break
            except websockets.WebSocketException as wse:
                logging.warn(wse)
                self._ws = None
                self._retries += 1
                await asyncio.sleep(self._retry_wait * self._retry)
        else:
            raise ConnectionError("Max Retries Exceeded")

    async def subscribe(self, channels):
        '''Start subscribing to channels.
        If the necessary connection isn't open yet, it opens now.
        '''
        ws_channels = []
        polygon_channels = []
        for c in channels:
            if c.startswith(('Q.', 'T.', 'A.', 'AM.',)):
                polygon_channels.append(c)
            else:
                ws_channels.append(c)

        if len(ws_channels) > 0:
            await self._ensure_ws()
            self._streams |= set(ws_channels)
            await self._ws.send(json.dumps({
                'action': 'listen',
                'data': {
                    'streams': ws_channels,
                }
            }))

        if len(polygon_channels) > 0:
            await self._ensure_polygon()
            await self.polygon.subscribe(polygon_channels)

    async def unsubscribe(self, channels):
        '''Handle un-subscribing from channels.
        '''
        if not self._ws:
            return

        ws_channels = []
        polygon_channels = []
        for c in channels:
            if c.startswith(('Q.', 'T.', 'A.', 'AM.',)):
                polygon_channels.append(c)
            else:
                ws_channels.append(c)

        if len(ws_channels) > 0:
            # Currently our streams don't support unsubscribe
            # not as useful with our feeds
            pass

        if len(polygon_channels) > 0:
            await self.polygon.unsubscribe(polygon_channels)

    def run(self, initial_channels=[]):
        '''Run forever and block until exception is raised.
        initial_channels is the channels to start with.
        '''
        loop = self.loop
        try:
            loop.run_until_complete(self.subscribe(initial_channels))
            loop.run_forever()
        except KeyboardInterrupt:
            logging.info("Exiting on Interrupt")
        finally:
            loop.run_until_complete(self.close())
            loop.close()

    async def close(self):
        '''Close any of open connections'''
        if self._ws is not None:
            await self._ws.close()
            self._ws = None
        if self.polygon is not None:
            await self.polygon.close()
            self.polygon = None

    def _cast(self, channel, msg):
        if channel == 'account_updates':
            return Account(msg)
        return Entity(msg)

    async def _dispatch(self, channel, msg):
        for pat, handler in self._handlers.items():
            if pat.match(channel):
                ent = self._cast(channel, msg['data'])
                await handler(self, channel, ent)

    def on(self, channel_pat, symbols=None):
        def decorator(func):
            self.register(channel_pat, func, symbols)
            return func

        return decorator

    def register(self, channel_pat, func, symbols=None):
        if not asyncio.iscoroutinefunction(func):
            raise ValueError('handler must be a coroutine function')
        if isinstance(channel_pat, str):
            channel_pat = re.compile(channel_pat)
        self._handlers[channel_pat] = func
        self._handler_symbols[func] = symbols
        if self.polygon:
            self.polygon.register(channel_pat, func, symbols)

    def deregister(self, channel_pat):
        if isinstance(channel_pat, str):
            channel_pat = re.compile(channel_pat)
        self._handler_symbols.pop(self._handlers[channel_pat], None)
        del self._handlers[channel_pat]
        if self.polygon:
            self.polygon.deregister(channel_pat)
