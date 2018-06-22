import asyncio
import json
import re
import websockets
from .common import get_base_url, get_credentials
from .rest import Account, AssetBars, Quote, Entity
from . import polygon


class StreamConn(object):
    def __init__(self, key_id=None, secret_key=None, base_url=None):
        self._key_id, self._secret_key = get_credentials(key_id, secret_key)
        base_url = re.sub(r'^http', 'ws', base_url or get_base_url())
        self._endpoint = base_url + '/stream'
        self._handlers = {}
        self._base_url = base_url
        self._ws = None
        self.polygon = None

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
        msg = json.loads(r)
        # TODO: check unauthorized
        self._ws = ws
        await self._dispatch('authenticated', msg)

        async def consume_msg():
            try:
                while True:
                    r = await ws.recv()
                    msg = json.loads(r)
                    stream = msg.get('stream')
                    if stream is not None:
                        await self._dispatch(stream, msg)
            finally:
                await ws.close()
                self._ws = None
        asyncio.ensure_future(consume_msg())
        return ws

    async def _ensure_nats(self):
        if self.polygon is not None:
            return
        self.polygon = polygon.Stream(self._key_id)
        self.polygon.register(r'.*', self._dispatch_nats)
        await self.polygon.connect()

    async def _ensure_ws(self):
        if self._ws is not None:
            return
        self._ws = await self._connect()

    async def subscribe(self, channels):
        '''Start subscribing channels.
        If the necessary connection isn't open yet, it opens now.
        '''
        ws_channels = []
        nats_channels = []
        for c in channels:
            if c.startswith(('Q.', 'T.', 'A.', 'AM.',)):
                nats_channels.append(c)
            else:
                ws_channels.append(c)

        if len(ws_channels) > 0:
            await self._ensure_ws()
            await self._ws.send(json.dumps({
                'action': 'listen',
                'data': {
                    'streams': ws_channels,
                }
            }))

        if len(nats_channels) > 0:
            await self._ensure_nats()
            await self.polygon.subscribe(nats_channels)

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
        if self.polygon is not None:
            await self.polygon.close()

    def _cast(self, stream, msg):
        if stream == 'account_updates':
            return Account(msg)
        elif re.match(r'^bars/', stream):
            return AssetBars(msg)
        elif re.match(r'^quotes/', stream):
            return Quote(msg)
        return Entity(msg)

    async def _dispatch_nats(self, conn, subject, data):
        for pat, handler in self._handlers.items():
            if pat.match(subject):
                await handler(self, subject, data)

    async def _dispatch(self, stream, msg):
        for pat, handler in self._handlers.items():
            if pat.match(stream):
                ent = self._cast(stream, msg['data'])
                await handler(self, stream, ent)

    def on(self, stream_pat):
        def decorator(func):
            self.register(stream_pat, func)
            return func

        return decorator

    def register(self, stream_pat, func):
        if not asyncio.iscoroutinefunction(func):
            raise ValueError('handler must be a coroutine function')
        if isinstance(stream_pat, str):
            stream_pat = re.compile(stream_pat)
        self._handlers[stream_pat] = func

    def deregister(self, stream_pat):
        if isinstance(stream_pat, str):
            stream_pat = re.compile(stream_pat)
        del self._handlers[stream_pat]
