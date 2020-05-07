import asyncio
import json
import time
import re
import os
import websockets
from .entity import (
    Quote, Trade, Agg, Entity,
    trade_mapping, quote_mapping, agg_mapping
)
from alpaca_trade_api.common import get_polygon_credentials
import logging


class StreamConn(object):
    def __init__(self, key_id=None):
        self._key_id = get_polygon_credentials(key_id)
        self._endpoint = os.environ.get(
            'POLYGON_WS_URL',
            'wss://alpaca.socket.polygon.io/stocks'
        ).rstrip('/')
        self._handlers = {}
        self._handler_symbols = {}
        self._streams = set([])
        self._ws = None
        self._retry = int(os.environ.get('APCA_RETRY_MAX', 3))
        self._retry_wait = int(os.environ.get('APCA_RETRY_WAIT', 3))
        self._retries = 0
        self.loop = asyncio.get_event_loop()
        self._consume_task = None

    async def connect(self):
        await self._dispatch({'ev': 'status',
                              'status': 'connecting',
                              'message': 'Connecting to Polygon'})
        self._ws = await websockets.connect(self._endpoint)
        self._stream = self._recv()

        msg = await self._next()
        if msg.get('status') != 'connected':
            raise ValueError(
                ("Invalid response on Polygon websocket connection: {}"
                    .format(msg))
            )
        await self._dispatch(msg)
        if await self.authenticate():
            self._consume_task = asyncio.ensure_future(self._consume_msg())
        else:
            await self.close()

    async def authenticate(self):
        ws = self._ws
        if not ws:
            return False

        await ws.send(json.dumps({
            'action': 'auth',
            'params': self._key_id
        }))
        data = await self._next()
        stream = data.get('ev')
        msg = data.get('message')
        status = data.get('status')
        if (stream == 'status'
                and msg == 'authenticated'
                and status == 'auth_success'):
            # reset retries only after we successfully authenticated
            self._retries = 0
            await self._dispatch(data)
            return True
        else:
            raise ValueError('Invalid Polygon credentials, '
                             f'Failed to authenticate: {data}')

    async def _next(self):
        '''Returns the next message available
        '''
        return await self._stream.__anext__()

    async def _recv(self):
        '''Function used to recieve and parse all messages from websocket stream.

        This generator yields one message per each call.
        '''
        try:
            while True:
                r = await self._ws.recv()
                if isinstance(r, bytes):
                    r = r.decode('utf-8')
                msg = json.loads(r)
                for update in msg:
                    yield update
        except Exception as e:
            await self._dispatch({'ev': 'status',
                                  'status': 'disconnected',
                                  'message':
                                  f'Polygon Disconnected Unexpectedly ({e})'})
            await self.close()
            asyncio.ensure_future(self._ensure_ws())

    async def consume(self):
        if self._consume_task:
            await self._consume_task

    async def _consume_msg(self):
        async for data in self._stream:
            stream = data.get('ev')
            if stream:
                await self._dispatch(data)
            elif data.get('status') == 'disconnected':
                # Polygon returns this on an empty 'ev' id..
                data['ev'] = 'status'
                await self._dispatch(data)
                raise ConnectionResetError(
                    'Polygon terminated connection: '
                    f'({data.get("message")})')

    async def _ensure_ws(self):
        if self._ws is not None:
            return

        while self._retries <= self._retry:
            try:
                await self.connect()
                if self._streams:
                    await self.subscribe(self._streams)
                break
            except Exception as e:
                await self._dispatch({'ev': 'status',
                                      'status': 'connect failed',
                                      'message':
                                      f'Polygon Connection Failed ({e})'})
                self._ws = None
                self._retries += 1
                time.sleep(self._retry_wait * self._retry)
        else:
            raise ConnectionError("Max Retries Exceeded")

    async def subscribe(self, channels):
        '''Subscribe to channels.
        Note: This is cumulative, meaning you can add channels at runtime,
        and you do not need to specify all the channels.

        To remove channels see unsubscribe().

        If the necessary connection isn't open yet, it opens now.
        '''
        if len(channels) > 0:
            await self._ensure_ws()
            # Join channel list to string
            streams = ','.join(channels)
            self._streams |= set(channels)
            await self._ws.send(json.dumps({
                'action': 'subscribe',
                'params': streams
            }))

    async def unsubscribe(self, channels):
        '''Unsubscribe from channels
        '''
        if not self._ws:
            return
        if len(channels) > 0:
            # Join channel list to string
            streams = ','.join(channels)
            self._streams -= set(channels)
            await self._ws.send(json.dumps({
                'action': 'unsubscribe',
                'params': streams
            }))

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
        '''Close any open connections'''
        if self._consume_task:
            self._consume_task.cancel()
        if self._ws is not None:
            await self._ws.close()
        self._ws = None

    def _cast(self, subject, data):
        if subject == 'T':
            return Trade({trade_mapping[k]: v for k,
                          v in data.items() if k in trade_mapping})
        if subject == 'Q':
            return Quote({quote_mapping[k]: v for k,
                          v in data.items() if k in quote_mapping})
        if subject == 'AM' or subject == 'A':
            return Agg({agg_mapping[k]: v for k,
                        v in data.items() if k in agg_mapping})
        return Entity(data)

    async def _dispatch(self, msg):
        channel = msg.get('ev')
        for pat, handler in self._handlers.items():
            if pat.match(channel):
                handled_symbols = self._handler_symbols.get(handler)
                if handled_symbols is None or msg['sym'] in handled_symbols:
                    ent = self._cast(channel, msg)
                    await handler(self, channel, ent)

    def register(self, channel_pat, func, symbols=None):
        if not asyncio.iscoroutinefunction(func):
            raise ValueError('handler must be a coroutine function')
        if isinstance(channel_pat, str):
            channel_pat = re.compile(channel_pat)
        self._handlers[channel_pat] = func
        self._handler_symbols[func] = symbols

    def deregister(self, channel_pat):
        if isinstance(channel_pat, str):
            channel_pat = re.compile(channel_pat)
        self._handler_symbols.pop(self._handlers[channel_pat], None)
        del self._handlers[channel_pat]
