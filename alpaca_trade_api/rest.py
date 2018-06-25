import logging
import os
import requests
from requests.exceptions import HTTPError
import time
from .common import get_base_url, get_credentials
from .entity import (
    Account, Asset, Order, Position,
    AssetBars, Quote, Fundamental,
    Clock, Calendar,
)
from . import polygon

logger = logging.getLogger(__name__)


class RetryException(Exception):
    pass


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
        self._retry = int(os.environ.get('APCA_MAX_RETRY', 3))
        self._retry_wait = int(os.environ.get('APCA_RETRY_WAIT', 3))
        self.polygon = polygon.REST(self._key_id)

    def _request(self, method, path, data=None, prefix='/v1'):
        url = self._base_url + prefix + path
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

        retry = self._retry
        if retry < 0:
            retry = 0
        while retry >= 0:
            try:
                return self._one_request(method, url, opts, retry)
            except RetryException:
                retry_wait = self._retry_wait
                logger.warn(
                    'sleep {} seconds and retrying {} '
                    '{} more time(s)...'.format(
                        retry_wait, url, retry))
                time.sleep(retry_wait)
                retry -= 1
                continue

    def _one_request(self, method, url, opts, retry):
        '''
        Perform one request, possibly raising RetryException in the case
        the response is 429. Otherwise, if error text contain "code" string,
        then it decodes to json object and returns APIError.
        Returns the body json in the 200 status.
        '''
        resp = self._session.request(method, url, **opts)
        try:
            resp.raise_for_status()
        except HTTPError:
            # retry if we hit Rate Limit
            if resp.status_code == 429 and retry > 0:
                raise RetryException()
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

    def get_account(self):
        '''Get the account'''
        resp = self.get('/account')
        return Account(resp)

    def list_orders(self, status=None):
        '''Get a list of orders'''
        params = dict()
        if status is not None:
            params['status'] = status
        resp = self.get('/orders', params)
        return [Order(o) for o in resp]

    def submit_order(self, symbol, qty, side, type, time_in_force,
                     limit_price=None, stop_price=None, client_order_id=None):
        '''Request a new order'''
        params = {
            'symbol': symbol,
            'qty': qty,
            'side': side,
            'type': type,
            'time_in_force': time_in_force,
        }
        if limit_price is not None:
            params['limit_price'] = limit_price
        if stop_price is not None:
            params['stop_price'] = stop_price
        if client_order_id is not None:
            params['client_order_id'] = client_order_id
        resp = self.post('/orders', params)
        return Order(resp)

    def get_order_by_client_order_id(self, client_order_id):
        '''Get an order by client order id'''
        resp = self.get('/orders:by_client_order_id', {
            'client_order_id': client_order_id,
        })
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

    def list_assets(self, status=None, asset_class=None):
        '''Get a list of assets'''
        params = {
            'status': status,
            'assert_class': asset_class,
        }
        resp = self.get('/assets', params)
        return [Asset(o) for o in resp]

    def get_asset(self, symbol):
        '''Get an asset'''
        resp = self.get('/assets/{}'.format(symbol))
        return Asset(resp)

    def list_quotes(self, symbols):
        '''Get a list of quotes'''
        if not isinstance(symbols, str):
            symbols = ','.join(symbols)
        params = {
            'symbols': symbols,
        }
        resp = self.get('/quotes', params)
        return [Quote(o) for o in resp]

    def get_quote(self, symbol):
        '''Get a quote'''
        resp = self.get('/assets/{}/quote'.format(symbol))
        return Quote(resp)

    def list_fundamentals(self, symbols):
        '''Get a list of fundamentals'''
        if not isinstance(symbols, str):
            symbols = ','.join(symbols)
        params = {
            'symbols': symbols,
        }
        resp = self.get('/fundamentals', params)
        return [Fundamental(o) for o in resp]

    def get_fundamental(self, symbol):
        '''Get a fundamental'''
        resp = self.get('/assets/{}/fundamental'.format(symbol))
        return Fundamental(resp)

    def list_bars(
            self,
            symbols,
            timeframe,
            start_dt=None,
            end_dt=None,
            limit=None):
        '''Get a list of bars'''
        if not isinstance(symbols, str):
            symbols = ','.join(symbols)
        params = {
            'symbols': symbols,
            'timeframe': timeframe,
        }
        if start_dt is not None:
            params['start_dt'] = start_dt
        if end_dt is not None:
            params['end_dt'] = end_dt
        if limit is not None:
            params['limit'] = limit
        resp = self.get('/bars', params)
        return [AssetBars(o) for o in resp]

    def get_bars(
            self,
            symbol,
            timeframe,
            start_dt=None,
            end_dt=None,
            limit=None):
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
        resp = self.get('/assets/{}/bars'.format(symbol), params)
        return AssetBars(resp)

    def get_clock(self):
        resp = self.get('/clock')
        return Clock(resp)

    def get_calendar(self, start=None, end=None):
        params = {}
        if start is not None:
            params['start'] = start
        if end is not None:
            params['end'] = end
        resp = self.get('/calendar', data=params)
        return [Calendar(o) for o in resp]
