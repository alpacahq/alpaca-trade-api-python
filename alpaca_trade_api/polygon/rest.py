import requests
from .entity import (
    Aggs,
    Trade, Trades,
    Quote, Quotes,
    Exchange, SymbolTypeMap, ConditionMap,
)


class REST(object):

    def __init__(self, api_key, isStaging = False):
        self._api_key = api_key
        self.isStaging = isStaging
        self._session = requests.Session()

    def _request(self, method, path, params=None):
        url = 'https://api.polygon.io/v1' + path
        params = params or {}
        params['apiKey'] = self._api_key
        if self.isStaging:
            params['staging'] = True
        resp = self._session.request(method, url, params=params)
        resp.raise_for_status()
        return resp.json()

    def get(self, path, params=None):
        return self._request('GET', path, params=params)

    def exchanges(self):
        path = '/meta/exchanges'
        return [Exchange(o) for o in self.get(path)]

    def symbol_type_map(self):
        path = '/meta/symbol-types'
        return SymbolTypeMap(self.get(path))

    def historic_trades(self, symbol, date, offset=None, limit=None):
        path = '/historic/trades/{}/{}'.format(symbol, date)
        params = {}
        if offset is not None:
            params['offset'] = offset
        if limit is not None:
            params['limit'] = limit
        raw = self.get(path, params)

        return Trades(raw)

    def historic_quotes(self, symbol, date, offset=None, limit=None):
        path = '/historic/quotes/{}/{}'.format(symbol, date)
        params = {}
        if offset is not None:
            params['offset'] = offset
        if limit is not None:
            params['limit'] = limit
        raw = self.get(path, params)

        return Quotes(raw)

    def historic_agg(self, size, symbol,
                     _from=None, to=None, limit=None):
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
        path = '/last_quote/stocks/{}'.format(symbol)
        raw = self.get(path)
        # TODO status check
        return Quote(raw['last'])

    def condition_map(self, ticktype='trades'):
        path = '/meta/conditions/{}'.format(ticktype)
        return ConditionMap(self.get(path))
