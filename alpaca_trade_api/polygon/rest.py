import requests
import pandas as pd
from .entity import (
    Agg, Aggs,
    Trade, Quote
)


class REST(object):

    def __init__(self, key_id):
        self._key_id = key_id
        self._session = requests.Session()

    def _request(self, method, path, params=None):
        url = 'https://api.polygon.io/v1' + path
        params = params or {}
        params['apiKey'] = self._key_id
        resp = self._session.request(method, url, params=params)
        resp.raise_for_status()
        return resp.json()

    def get(self, path, params=None):
        return self._request('GET', path, params=params)

    def historic_quotes(self, symbol, date, offset=None, limit=None):
        path = '/historic/quotes/{}/{}'.format(symbol, date)
        params = {}
        if offset is not None:
            params['offset'] = offset
        if limit is not None:
            params['limit'] = limit
        raw = self.get(path, params)

        df = pd.DataFrame(sorted(raw['ticks'], key=lambda d: d['t']), columns=('t', 'c', 'bE', 'aE', 'aP', 'bP', 'bS', 'aS'))
        df.columns = [raw['map'][c] for c in df.columns]
        df.set_index('timestamp', inplace=True)
        df.index = pd.to_datetime(df.index.astype('int64') * 1000000, utc=True).tz_convert('America/New_York')
        return df

    def historic_agg(self, size, symbol, _from=None, to=None, limit=None):
        path = '/historic/agg/{}/{}'.format(size, symbol)
        params = {}
        if _from is not None:
            params['from'] = _from
        if to is not None:
            params['to'] = to
        if limit is not None:
            params['limit'] = limit
        raw = self.get(path, params)

        return Aggs(raw)

    def last_trade(self, symbol):
        path = '/last/stocks/{}'.format(symbol)
        raw = self.get(path)
        return Trade(raw['last'])

    def last_quote(self, symbol):
        path = '/last_quotes/{}'.format(symbol)
        raw = self.get(path)
        # TODO status check
        return Quote(raw['last'])