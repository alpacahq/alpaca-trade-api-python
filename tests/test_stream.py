import alpaca_trade_api as tradeapi
import json
import pytest
try:
  from unittest.mock import patch
except ImportError:
  from mock import patch
from websocket import WebSocketConnectionClosedException


@patch('websocket.WebSocket')
def test_stream(WebSocket):
    class Fake(object):
        def __init__(self):
            self._state = 'init'

        def _start_streaming(self):
            for i in range(3):
                for stream in self._streams:
                    yield stream

        def send(self, jmsg):
            msg = json.loads(jmsg)

            if self._state == 'init':
                assert msg['action'] == 'authenticate'
                self._state = 'authenticated'
            elif msg['action'] == 'listen':
                assert self._state == 'authenticated'
                self._streams = msg['data']['streams']
                self._state = 'streaming'
                self._streamer = self._start_streaming()

        def recv(self):

            if self._state == 'authenticated':
                return json.dumps({
                    'stream': 'authentication',
                    'data': {
                        'status': 'authenticated',
                    }
                }).encode()
            elif self._state == 'streaming':
                try:
                    stream = next(self._streamer)
                except StopIteration:
                    raise WebSocketConnectionClosedException()
                if stream == 'account_updates':
                    return json.dumps({
                        "stream": stream,
                        "data": {
                            "id": "ef505a9a-2f3c-4b8a-be95-6b6f185f8a03",
                            "created_at": "2018-02-26T19:22:31Z",
                            "updated_at": "2018-02-27T18:16:24Z",
                            "deleted_at": None,
                            "status": "ACTIVE",
                            "currency": "USD",
                            "amount_tradable": "1241.54",
                            "amount_withdrawable": "523.71"
                        }
                    })
                elif stream.startswith('quotes/'):
                    return json.dumps({
                        "stream": stream,
                        "data": {
                            "bid_timestamp": "2018-02-28T21:16:58.704+0000",
                            "bid": 178.22,
                            "ask_timestamp": "2018-02-28T21:16:58.704+0000",
                            "ask": 178.23,
                            "last_timestamp": "2018-02-28T21:16:58.704+0000",
                            "last": 178.22,
                            "day_change": 0.008050799,
                            "symbol": "AAPL"
                        },
                    })
            else:
                raise AssertionError('unexpected')
    fake = Fake()
    ws = WebSocket()
    ws.send.side_effect = fake.send
    ws.recv.side_effect = fake.recv
    conn = tradeapi.StreamConn('account_id', 'api_key')

    @conn.on('authenticated')
    def on_auth(conn, stream, msg):
        conn.subscribe([
            'account_updates',
            'quotes/AAPL',
        ])

    @conn.on(r'^bars/')
    def on_bars(conn, stream, msg):
        assert stream == 'quotes/AAPL'

    with pytest.raises(WebSocketConnectionClosedException):
        conn.run()
