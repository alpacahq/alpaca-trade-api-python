import requests
from .entity import (
    Aggs, Aggsv2, Aggsv2Set,
    Trade, Trades,
    Quote, Quotes,
    Exchange, SymbolTypeMap, ConditionMap,
    Company, Dividends, Splits, Earnings, Financials, NewsList, Ticker
)


def _is_list_like(o):
    return isinstance(o, (list, set, tuple))


class REST(object):

    def __init__(self, api_key, staging=False):
        self._api_key = api_key
        self._staging = staging
        self._session = requests.Session()

    def _request(self, method, path, params=None, version='v1'):
        url = 'https://api.polygon.io/' + version + path
        params = params or {}
        params['apiKey'] = self._api_key
        if self._staging:
            params['staging'] = 'true'
        resp = self._session.request(method, url, params=params)
        resp.raise_for_status()
        return resp.json()

    def get(self, path, params=None, version='v1'):
        return self._request('GET', path, params=params, version=version)

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

    def historic_agg_v2(self, symbol, multiplier, timespan, _from, to,
                        unadjusted=False):
        path = '/aggs/ticker/{}/range/{}/{}/{}/{}'.format(
            symbol, multiplier, timespan, _from, to
        )
        params = {}
        params['unadjusted'] = unadjusted
        raw = self.get(path, params, version='v2')
        return Aggsv2(raw)

    def grouped_daily(self, date, unadjusted=False):
        path = '/aggs/grouped/locale/US/market/STOCKS/{}'.format(date)
        params = {}
        params['unadjusted'] = unadjusted
        raw = self.get(path, params, version='v2')
        return Aggsv2Set(raw)

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

    def company(self, symbol):
        return self._get_symbol(symbol, 'company', Company)

    def _get_symbol(self, symbol, resource, entity):
        multi = _is_list_like(symbol)
        symbols = symbol if multi else [symbol]
        if len(symbols) > 50:
            raise ValueError('too many symbols: {}'.format(len(symbols)))
        params = {
            'symbols': ','.join(symbols),
        }
        path = '/meta/symbols/{}'.format(resource)
        res = self.get(path, params=params)
        if isinstance(res, list):
            res = {o['symbol']: o for o in res}
        retmap = {sym: entity(res[sym]) for sym in symbols if sym in res}
        if not multi:
            return retmap.get(symbol)
        return retmap

    def dividends(self, symbol):
        return self._get_symbol(symbol, 'dividends', Dividends)

    def splits(self, symbol):
        path = '/meta/symbols/{}/splits'.format(symbol)
        return Splits(self.get(path))

    def earnings(self, symbol):
        return self._get_symbol(symbol, 'earnings', Earnings)

    def financials(self, symbol):
        return self._get_symbol(symbol, 'financials', Financials)

    def news(self, symbol):
        path = '/meta/symbols/{}/news'.format(symbol)
        return NewsList(self.get(path))

    def all_tickers(self):
        path = '/snapshot/locale/us/markets/stocks/tickers'
        return [
            Ticker(ticker) for ticker in
            self.get(path, version='v2')['tickers']
        ]

    def snapshot(self, symbol):
        path = '/snapshot/locale/us/markets/stocks/tickers/{}'.format(symbol)
        return Ticker(self.get(path, version='v2'))
