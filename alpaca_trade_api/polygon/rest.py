import dateutil
import requests
from .entity import (
    Aggsv2, Aggsv2Set,
    Trade, Trades, TradesV2,
    Quote, Quotes, QuotesV2,
    Exchange, SymbolTypeMap, ConditionMap,
    Company, Dividends, Splits, Earnings, Financials, NewsList, Ticker,
    DailyOpenClose
)
from alpaca_trade_api.common import get_polygon_credentials
from deprecated import deprecated


def _is_list_like(o):
    return isinstance(o, (list, set, tuple))


class REST(object):

    def __init__(self, api_key, staging=False):
        self._api_key = get_polygon_credentials(api_key)
        self._staging = staging
        self._session = requests.Session()

    def _request(self, method, path, params=None, version='v1'):
        url = 'https://api.polygon.io/' + version + path
        params = params or {}
        params['apiKey'] = self._api_key
        if self._staging:
            params['apiKey'] += '-staging'
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

    @deprecated(
        'historic_trades v1 is deprecated and will be removed from the ' +
        'Polygon API in the future. Please upgrade to historic_trades_v2.'
    )
    def historic_trades(self, symbol, date, offset=None, limit=None):
        path = '/historic/trades/{}/{}'.format(symbol, date)
        params = {}
        if offset is not None:
            params['offset'] = offset
        if limit is not None:
            params['limit'] = limit
        raw = self.get(path, params)

        return Trades(raw)

    def historic_trades_v2(
            self, symbol, date, timestamp=None, timestamp_limit=None,
            reverse=None, limit=None
    ):
        path = '/ticks/stocks/trades/{}/{}'.format(symbol, date)
        params = {}
        if timestamp is not None:
            params['timestamp'] = timestamp
        if timestamp_limit is not None:
            params['timestampLimit'] = timestamp_limit
        if reverse is not None:
            params['reverse'] = reverse
        if limit is not None:
            params['limit'] = limit
        raw = self.get(path, params, 'v2')

        return TradesV2(raw)

    @deprecated(
        'historic_quotes v1 is deprecated and will be removed from the ' +
        'Polygon API in the future. Please upgrade to historic_quotes_v2.'
    )
    def historic_quotes(self, symbol, date, offset=None, limit=None):
        path = '/historic/quotes/{}/{}'.format(symbol, date)
        params = {}
        if offset is not None:
            params['offset'] = offset
        if limit is not None:
            params['limit'] = limit
        raw = self.get(path, params)

        return Quotes(raw)

    def historic_quotes_v2(
            self, symbol, date, timestamp=None, timestamp_limit=None,
            reverse=None, limit=None
    ):
        path = '/ticks/stocks/nbbo/{}/{}'.format(symbol, date)
        params = {}
        if timestamp is not None:
            params['timestamp'] = timestamp
        if timestamp_limit is not None:
            params['timestampLimit'] = timestamp_limit
        if reverse is not None:
            params['reverse'] = reverse
        if limit is not None:
            params['limit'] = limit
        raw = self.get(path, params, 'v2')

        return QuotesV2(raw)

    def historic_agg_v2(self, symbol, multiplier, timespan, _from, to,
                        unadjusted=False, limit=None):
        """

        :param symbol:
        :param multiplier: Size of the timespan multiplier (distance between
               samples. e.g if it's 1 we get for daily 2015-01-05, 2015-01-06,
                            2015-01-07, 2015-01-08.
                            if it's 3 we get 2015-01-01, 2015-01-04,
                            2015-01-07, 2015-01-10)
        :param timespan: Size of the time window: minute, hour, day, week,
               month, quarter, year
        :param _from: some use isoformat some use timestamp. for now we
                      handle both.
                      examples of different usages: pylivetrader,
                      alpaca-backtrader.
        :param to:
        :param unadjusted:
        :param limit: max samples to retrieve (seems like we get "limit - 1" )
        :return:
        """
        path_template = '/aggs/ticker/{symbol}/range/{multiplier}/' \
                        '{timespan}/{_from}/{to}'
        if isinstance(_from, int):
            path = path_template.format(symbol=symbol,
                                        multiplier=multiplier,
                                        timespan=timespan,
                                        _from=_from,
                                        to=to
                                        )
        else:
            path = path_template.format(symbol=symbol,
                                        multiplier=multiplier,
                                        timespan=timespan,
                                        _from=dateutil.parser.parse(
                                            _from).date().isoformat(),
                                        to=dateutil.parser.parse(
                                            to).date().isoformat()
                                        )
        params = {'unadjusted': unadjusted}
        if limit:
            params['limit'] = limit
        raw = self.get(path, params, version='v2')
        return Aggsv2(raw)

    def grouped_daily(self, date, unadjusted=False):
        path = '/aggs/grouped/locale/US/market/STOCKS/{}'.format(date)
        params = {}
        params['unadjusted'] = unadjusted
        raw = self.get(path, params, version='v2')
        return Aggsv2Set(raw)

    def daily_open_close(self, symbol, date):
        path = '/open-close/{}/{}'.format(symbol, date)
        raw = self.get(path)
        return DailyOpenClose(raw)

    def last_trade(self, symbol):
        path = '/last/stocks/{}'.format(symbol)
        raw = self.get(path)
        return Trade(raw['last'])

    def last_quote(self, symbol):
        path = '/last_quote/stocks/{}'.format(symbol)
        raw = self.get(path)
        # TODO status check
        return Quote(raw['last'])

    def previous_day_bar(self, symbol):
        path = '/aggs/ticker/{}/prev'.format(symbol)
        raw = self.get(path, version='v2')
        return Aggsv2(raw)

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

    def gainers_losers(self, direction="gainers"):
        path = '/snapshot/locale/us/markets/stocks/{}'.format(direction)
        return [
            Ticker(ticker) for ticker in
            self.get(path, version='v2')['tickers']
        ]

    def all_tickers(self):
        path = '/snapshot/locale/us/markets/stocks/tickers'
        return [
            Ticker(ticker) for ticker in
            self.get(path, version='v2')['tickers']
        ]

    def snapshot(self, symbol):
        path = '/snapshot/locale/us/markets/stocks/tickers/{}'.format(symbol)
        return Ticker(self.get(path, version='v2'))
