import json
import re
import websocket
from .common import get_base_url


class StreamConn(object):
    def __init__(self, account_id, api_key):
        self._account_id = account_id
        self._api_key = api_key
        base_url = re.sub(r'^http', 'ws', get_base_url())
        self._endpoint = base_url + '/stream'
        self._handlers = {}

    def _connect(self):
        ws = websocket.WebSocket()
        ws.connect(self._endpoint)
        ws.send(json.dumps({
            'action': 'authenticate',
            'data': {
                'account_id': self._account_id,
                'key': self._api_key
            }
        }))
        r = ws.recv()
        msg = json.loads(r)
        # check unauthorized
        self._ws = ws
        self._dispatch('authenticated', msg)
        return ws

    def subscribe(self, streams):
        self._ws.send(json.dumps({
            'action': 'listen',
            'data': {
                'streams': streams,
            }
        }))

    def run(self):
        ws = self._connect()
        try:
            while True:
                r = ws.recv()
                msg = json.loads(r)
                stream = msg.get('stream')
                if stream is not None:
                    self._dispatch(stream, msg)
        finally:
            ws.close()

    def _dispatch(self, stream, msg):
        for pat, handler in self._handlers.items():
            if pat.match(stream):
                handler(self, stream, msg)

    def on(self, stream_pat):
        def decorator(func):
            self.register(stream_pat, func)
            return func

        return decorator

    def register(self, stream_pat, func):
        if isinstance(stream_pat, str):
            stream_pat = re.compile(stream_pat)
        self._handlers[stream_pat] = func

    def deregister(self, stream_pat):
        if isinstance(stream_pat, str):
            stream_pat = re.compile(stream_pat)
        del self._handlers[stream_pat]
