"""
Stream V1
The new Alpaca data stream is under stream.py
"""
import asyncio
import json
import os
import re
import traceback
from asyncio import CancelledError
import queue

import websockets
from .common import get_base_url, get_data_url, get_credentials, URL
from .entity import Account, Entity, trade_mapping, agg_mapping, quote_mapping
from . import polygon
from .entity import Trade, Quote, Agg
import logging
from typing import List, Callable


class _StreamConn(object):
    def __init__(self, key_id: str,
                 secret_key: str,
                 base_url: URL,
                 oauth: str = None,
                 raw_data: bool = False):
        """
        :param raw_data: should we return stream data raw or wrap it with
                         Entity objects.
        """
        self._key_id = key_id
        self._secret_key = secret_key
        self._oauth = oauth
        self._base_url = re.sub(r'^http', 'ws', base_url)
        self._endpoint = self._base_url + '/stream'
        self._handlers = {}
        self._handler_symbols = {}
        self._streams = set([])
        self._ws = None
        self._retry = int(os.environ.get('APCA_RETRY_MAX', 3))
        self._retry_wait = int(os.environ.get('APCA_RETRY_WAIT', 3))
        self._retries = 0
        self._consume_task = None
        self._raw_data = raw_data

    async def _connect(self):
        message = {
            'action': 'authenticate',
            'data': {
                'oauth_token': self._oauth
            } if self._oauth else {
                'key_id': self._key_id,
                'secret_key': self._secret_key,
            }
        }

        ws = await websockets.connect(self._endpoint)
        await ws.send(json.dumps(message))
        r = await ws.recv()
        if isinstance(r, bytes):
            r = r.decode('utf-8')
        msg = json.loads(r)

        if msg.get('data', {}).get('status'):
            status = msg.get('data').get('status')
            if status != 'authorized':
                raise ValueError(
                    (f"Invalid Alpaca API credentials, Failed to "
                     f"authenticate: {msg}")
                )
            else:
                self._retries = 0
        elif msg.get('data', {}).get('error'):
            raise Exception(f"Error while connecting to {self._endpoint}:"
                            f"{msg.get('data').get('error')}")
        else:
            self._retries = 0

        self._ws = ws
        await self._dispatch('authorized', msg)
        logging.info(f"connected to: {self._endpoint}")
        self._consume_task = asyncio.ensure_future(self._consume_msg())

    async def consume(self):
        if self._consume_task:
            await self._consume_task

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
        if isinstance(channels, str):
            channels = [channels]
        if len(channels) > 0:
            await self._ensure_ws()
            self._streams |= set(channels)
            await self._ws.send(json.dumps({
                'action': 'listen',
                'data': {
                    'streams': channels,
                }
            }))

    async def unsubscribe(self, channels):
        if isinstance(channels, str):
            channels = [channels]
        if len(channels) > 0:
            await self._ws.send(json.dumps({
                'action': 'unlisten',
                'data': {
                    'streams': channels,
                }
            }))

    async def close(self):
        await self.cancel_task()
        if self._ws:
            await self._ws.close()
            self._ws = None

    async def cancel_task(self):
        if self._consume_task:
            self._consume_task.cancel()

    def _cast(self, channel, msg):
        if channel == 'account_updates':
            return Account(msg)
        if channel.startswith('T.'):
            return Trade({trade_mapping[k]: v for k,
                          v in msg.items() if k in trade_mapping})
        if channel.startswith('Q.'):
            return Quote({quote_mapping[k]: v for k,
                          v in msg.items() if k in quote_mapping})
        if channel.startswith('A.') or channel.startswith('AM.'):
            # to be compatible with REST Agg
            msg['t'] = msg['s']
            return Agg({agg_mapping[k]: v for k,
                        v in msg.items() if k in agg_mapping})
        return Entity(msg)

    async def _dispatch(self, channel, msg):
        for pat, handler in self._handlers.items():
            if pat.match(channel):
                if self._raw_data:
                    await handler(self, channel, msg)
                else:
                    ent = self._cast(channel, msg['data'])
                    await handler(self, channel, ent)

    def on(self, channel_pat, symbols=None):
        def decorator(func):
            self.register(channel_pat, func, symbols)
            return func

        return decorator

    def register(self, channel_pat, func: Callable, symbols=None):
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


class StreamConn(object):
    def __init__(
            self,
            key_id: str = None,
            secret_key: str = None,
            base_url: URL = None,
            data_url: URL = None,
            data_stream: str = None,
            debug: bool = False,
            oauth: str = None,
            raw_data: bool = False):
        """
        :param base_url: api.alpaca.markets
        :param data_url: data.alpaca.markets
        :param data_stream: alpacadatav1/polygon
        :param debug: should print exceptions?
        :param raw_data: should we return stream data raw or wrap it with
                         Entity objects.
        """
        self._key_id, self._secret_key, self._oauth = \
            get_credentials(key_id, secret_key, oauth)
        self._base_url = base_url or get_base_url()
        self._data_url = data_url or get_data_url()
        if data_stream is not None:
            if data_stream in ('alpacadatav1', 'polygon'):
                _data_stream = data_stream
            else:
                raise ValueError('invalid data_stream name {}'.format(
                    data_stream))
        else:
            _data_stream = 'alpacadatav1'
        self._data_stream = _data_stream
        self._debug = debug
        self._raw_data = raw_data
        self._stop_stream_queue = queue.Queue()

        self.trading_ws = _StreamConn(self._key_id,
                                      self._secret_key,
                                      self._base_url,
                                      self._oauth,
                                      raw_data=self._raw_data)

        if self._data_stream == 'polygon':
            # DATA_PROXY_WS is used for the alpaca-proxy-agent.
            # this is how we set the polygon ws to go through the proxy agent
            endpoint = os.environ.get("DATA_PROXY_WS", '')
            if endpoint:
                os.environ['POLYGON_WS_URL'] = endpoint
            self.data_ws = polygon.StreamConn(
                self._key_id + '-staging' if 'staging' in self._base_url else
                self._key_id,
                raw_data=self._raw_data
            )
            self._data_prefixes = (('Q.', 'T.', 'A.', 'AM.'))
        else:
            self.data_ws = _StreamConn(self._key_id,
                                       self._secret_key,
                                       self._data_url,
                                       self._oauth,
                                       raw_data=self._raw_data)
            self._data_prefixes = (
                ('Q.', 'T.', 'AM.', 'alpacadatav1/'))

        self._handlers = {}
        self._handler_symbols = {}

        try:
            self.loop = asyncio.get_event_loop()
        except websockets.WebSocketException as wse:
            logging.warn(wse)
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)

    async def _ensure_ws(self, conn):
        if conn._handlers:
            return
        conn._handlers = self._handlers.copy()
        conn._handler_symbols = self._handler_symbols.copy()
        if isinstance(conn, _StreamConn):
            await conn._connect()
        else:
            await conn.connect()

    async def subscribe(self, channels: List[str]):
        '''Start subscribing to channels.
        If the necessary connection isn't open yet, it opens now.
        This may raise ValueError if a channel is not recognized.
        '''
        trading_channels, data_channels = [], []

        for c in channels:
            if c in ('trade_updates', 'account_updates'):
                trading_channels.append(c)
            elif c.startswith(self._data_prefixes):
                data_channels.append(c)
            else:
                raise ValueError(
                    ('unknown channel {} (you may need to specify ' +
                     'the right data_stream)').format(c))

        if trading_channels:
            await self._ensure_ws(self.trading_ws)
            await self.trading_ws.subscribe(trading_channels)
        if data_channels:
            await self._ensure_ws(self.data_ws)
            await self.data_ws.subscribe(data_channels)

    async def unsubscribe(self, channels: List[str]):
        '''Handle unsubscribing from channels.'''

        data_channels = [
            c for c in channels
            if c.startswith(self._data_prefixes)
        ]

        if data_channels:
            await self.data_ws.unsubscribe(data_channels)

    async def consume(self):
        await asyncio.gather(
            self.trading_ws.consume(),
            self.data_ws.consume(),
        )

    def run(self, initial_channels: List[str] = []):
        '''Run forever and block until exception is raised.
        initial_channels is the channels to start with.
        '''
        loop = self.loop
        should_renew = True  # should renew connection if it disconnects
        while should_renew:
            try:
                if loop.is_closed():
                    self.loop = asyncio.new_event_loop()
                    loop = self.loop
                loop.run_until_complete(self.subscribe(initial_channels))
                loop.run_until_complete(self.consume())
            except KeyboardInterrupt:
                logging.info("Exiting on Interrupt")
                should_renew = False
            except Exception as e:
                m = 'consume cancelled' if isinstance(e, CancelledError) else e
                logging.error(f"error while consuming ws messages: {m}")
                if self._debug:
                    traceback.print_exc()
                if not self._stop_stream_queue.empty():
                    self._stop_stream_queue.get()
                    should_renew = False
                loop.run_until_complete(self.close(should_renew))
                if loop.is_running():
                    loop.close()

    async def close(self, renew):
        """
        Close any of open connections
        :param renew: should re-open connection?
        """
        if self.trading_ws is not None:
            await self.trading_ws.close()
            self.trading_ws = None
        if self.data_ws is not None:
            await self.data_ws.close()
            self.data_ws = None
        if renew:
            self.trading_ws = _StreamConn(self._key_id,
                                          self._secret_key,
                                          self._base_url,
                                          self._oauth,
                                          raw_data=self._raw_data)
            if self._data_stream == 'polygon':
                self.data_ws = polygon.StreamConn(
                    self._key_id + '-staging' if 'staging' in
                    self._base_url else self._key_id,
                    raw_data=self._raw_data)
            else:
                self.data_ws = _StreamConn(self._key_id,
                                           self._secret_key,
                                           self._data_url,
                                           self._oauth,
                                           raw_data=self._raw_data)

    async def stop_ws(self):
        """
        Signal the ws connections to stop listenning to api stream.
        """
        self._stop_stream_queue.put_nowait({"should_stop": True})
        if self.trading_ws is not None:
            logging.info("Stopping the trading websocket connection")
            await self.trading_ws.cancel_task()
        if self.data_ws is not None:
            logging.info("Stopping the data websocket connection")
            await self.data_ws.cancel_task()

    def on(self, channel_pat, symbols=None):
        def decorator(func):
            self.register(channel_pat, func, symbols)
            return func

        return decorator

    def register(self, channel_pat, func: Callable, symbols=None):
        if not asyncio.iscoroutinefunction(func):
            raise ValueError('handler must be a coroutine function')
        if isinstance(channel_pat, str):
            channel_pat = re.compile(channel_pat)
        self._handlers[channel_pat] = func
        self._handler_symbols[func] = symbols

        if self.trading_ws:
            self.trading_ws.register(channel_pat, func, symbols)
        if self.data_ws:
            self.data_ws.register(channel_pat, func, symbols)

    def deregister(self, channel_pat):
        if isinstance(channel_pat, str):
            channel_pat = re.compile(channel_pat)
        self._handler_symbols.pop(self._handlers[channel_pat], None)
        del self._handlers[channel_pat]

        if self.trading_ws:
            self.trading_ws.deregister(channel_pat)
        if self.data_ws:
            self.data_ws.deregister(channel_pat)
