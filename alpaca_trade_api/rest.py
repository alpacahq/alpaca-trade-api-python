import dateutil.parser
import pandas as pd
import pprint
import re
import requests
from requests.exceptions import HTTPError
from .common import get_base_url, get_credentials

ISO8601YMD = re.compile(r'\d{4}-\d{2}-\d{2}T')


class APIError(Exception):
    def __init__(self, error):
        super().__init__(error['message'])
        self._error = error

    @property
    def code(self):
        return self._error['code']


class REST(object):
    def __init__(self, key_id=None, secret_key=None, base_url=None):
        self._key_id, self._secret_key = get_credentials(key_id, secret_key)
        self._base_url = base_url or get_base_url()
        self._session = requests.Session()

    def _request(self, method, path, data=None):
        url = self._base_url + path
        headers = {
            'APCA-API-KEY-ID': self._key_id,
            'APCA-API-SECRET-KEY': self._secret_key,
        }
        opts = {
            'headers': headers,
        }
        if method.upper() == 'GET':
            opts['params'] = data
        else:
            opts['json'] = data
        resp = self._session.request(method, url, **opts)
        try:
            resp.raise_for_status()
        except HTTPError as exc:
            if 'code' in resp.text:
                error = resp.json()
                if 'code' in error:
                    raise APIError(error)
            else:
                raise
        if resp.text != '':
            return resp.json()
        return None

    def get(self, path, data=None):
        return self._request('GET', path, data)

    def post(self, path, data=None):
        return self._request('POST', path, data)

    def delete(self, path, data=None):
        return self._request('DELETE', path, data)

    def list_accounts(self):
        '''Get a list of accounts'''
        resp = self.get('/api/v1/accounts')
        return [Account(o, self) for o in resp]

    def list_assets(self, status=None, asset_class=None):
        '''Get a list of assets'''
        params = {
            'status': status,
            'assert_class': asset_class,
        }
        resp = self.get('/api/v1/assets', params)
        return [Asset(o, self) for o in resp]

    def get_asset(self, symbol):
        '''Get an asset'''
        resp = self.get('/api/v1/assets/{}'.format(symbol))
        return Asset(resp, self)

    def list_quotes(self, symbols):
        '''Get a list of quotes'''
        if not isinstance(symbols, str):
            symbols = ','.join(symbols)
        params = {
            'symbols': symbols,
        }
        resp = self.get('/api/v1/quotes', params)
        return [Quote(o) for o in resp]

    def list_fundamentals(self, symbols):
        '''Get a list of fundamentals'''
        if not isinstance(symbols, str):
            symbols = ','.join(symbols)
        params = {
            'symbols': symbols,
        }
        resp = self.get('/api/v1/fundamentals', params)
        return [Fundamental(o) for o in resp]


class Entity(object):
    def __init__(self, raw):
        self._raw = raw

    def __getattr__(self, key):
        if key in self._raw:
            val = self._raw[key]
            if (isinstance(val, str) and
                    (key.endswith('_at') or
                     key.endswith('_timestamp') or
                     key.endswith('_time')) and
                    ISO8601YMD.match(val)):
                return dateutil.parser.parse(val)
            else:
                return val
        return getattr(super(), key)

    def __repr__(self):
        return '{name}({raw})'.format(
            name=self.__class__.__name__,
            raw=pprint.pformat(self._raw, indent=4),
        )


class Account(Entity):

    def __init__(self, raw, api):
        super().__init__(raw)
        self._api = api
        self._account_id = raw['id']

    def _fullpath(self, path, v='1'):
        return '/api/v{}/accounts/{}{}'.format(v, self._account_id, path)

    def get(self, path, data=None):
        fullpath = self._fullpath(path)
        return self._api.get(fullpath, data)

    def post(self, path, data=None):
        fullpath = self._fullpath(path)
        return self._api.post(fullpath, data)

    def delete(self, path, data=None):
        fullpath = self._fullpath(path)
        return self._api.delete(fullpath, data)

    def list_orders(self, status=None):
        '''Get a list of orders'''
        params = dict()
        if status is not None:
            params['status'] = status
        resp = self.get('/orders', params)
        return [Order(o) for o in resp]

    def submit_order(self, symbol, shares, side, type, time_in_force,
                     limit_price=None, stop_price=None, client_order_id=None):
        '''Request a new order'''
        params = {
            'symbol': symbol,
            'shares': shares,
            'side': side,
            'type': type,
            'time_in_force': time_in_force,
        }
        if limit_price is None:
            params['limit_price'] = limit_price
        if stop_price is None:
            params['stop_price'] = stop_price
        if client_order_id is not None:
            params['client_order_id'] = client_order_id
        resp = self.post('/orders', params)
        return Order(resp)

    def get_order_by_client_order_id(self, client_order_id):
        '''Get an order by client order id'''
        resp = self.get('/orders', data={
            'client_order_id': client_order_id,
        },
        )
        return Order(resp)

    def get_order(self, order_id):
        '''Get an order'''
        resp = self.get('/orders/{}'.format(order_id))
        return Order(resp)

    def cancel_order(self, order_id):
        '''Cancel an order'''
        self.delete('/orders/{}'.format(order_id))

    def list_positions(self):
        '''Get a list of open positions'''
        resp = self.get('/positions')
        return [Position(o) for o in resp]

    def get_position(self, symbol):
        '''Get an open position'''
        resp = self.get('/positions/{}'.format(symbol))
        return Position(resp)


class Asset(Entity):
    def __init__(self, raw, api):
        super().__init__(raw)
        self._api = api
        self._asset_id = raw['id']

    def get(self, path, data=None):
        fullpath = '/api/v1/assets/{}{}'.format(self._asset_id, path)
        return self._api.get(fullpath, data)

    def get_bars(self, timeframe, start_dt=None, end_dt=None, limit=None):
        '''Get bars'''
        params = {
            'timeframe': timeframe,
        }
        if start_dt is not None:
            params['start_dt'] = start_dt
        if end_dt is not None:
            params['end_dt'] = end_dt
        if limit is not None:
            params['limit'] = limit
        resp = self.get('/bars', params)
        return AssetBars(resp)

    def get_quote(self):
        '''Get a quote'''
        resp = self.get('/quote')
        return Quote(resp)

    def get_fundamental(self):
        '''Get a fundamental'''
        resp = self.get('/fundamental')
        return Fundamental(resp)


class Order(Entity):
    pass


class Position(Entity):
    pass


class Bar(Entity):
    pass


class AssetBars(Entity):
    def __init__(self, raw):
        super().__init__(raw)
        t = []
        o = []
        h = []
        l = []
        c = []
        v = []
        bars = []
        for bar in raw['bars']:
            t.append(pd.Timestamp(bar['time']))
            o.append(bar['open'])
            h.append(bar['high'])
            l.append(bar['low'])
            c.append(bar['close'])
            v.append(bar['volume'])
            bars.append(Bar(bar))
        raw['bars'] = bars
        self._df = pd.DataFrame(dict(
            open=o,
            high=h,
            low=l,
            close=c,
            volume=v,
        ), index=t)

    @property
    def df(self):
        return self._df


class Quote(Entity):
    pass


class Fundamental(Entity):
    pass
