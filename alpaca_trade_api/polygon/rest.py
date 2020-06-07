from typing import List
import dateutil.parser
import requests
from .entity import (
    Aggsv2, Aggsv2Set,
    Trade, Trades, TradesV2,
    Quote, Quotes, QuotesV2,
    Exchange, SymbolTypeMap, ConditionMap,
    Company, Dividends, Splits, Earnings, Financials, NewsList, Ticker,
    DailyOpenClose
)
from alpaca_trade_api.common import get_polygon_credentials, URL, DATE
from deprecated import deprecated


Exchanges = List[Exchange]
Tickers = List[Ticker]


def _is_list_like(o) -> bool:
    """
    returns True if o is either a list, a set or a tuple
    that way we could accept ['AAPL', 'GOOG'] or ('AAPL', 'GOOG') etc.
    """
    return isinstance(o, (list, set, tuple))


class REST(object):

    def __init__(self, api_key: str, staging: bool = False):
        self._api_key: str = get_polygon_credentials(api_key)
        self._staging: bool = staging
        self._session = requests.Session()

    def _request(self, method: str, path: str, params: dict = None,
                 version: str = 'v1'):
        """
        :param method: GET, POST, ...
        :param path: url part path (without the domain name)
        :param params: dictionary with params of the request
        :param version: v1 or v2
        :return: response
        """
        url: URL = URL('https://api.polygon.io/' + version + path)
        params = params or {}
        params['apiKey'] = self._api_key
        if self._staging:
            params['apiKey'] += '-staging'
        resp = self._session.request(method, url, params=params)
        resp.raise_for_status()
        return resp.json()

    def get(self, path: str, params: dict = None, version: str = 'v1'):
        return self._request('GET', path, params=params, version=version)

    def exchanges(self) -> Exchanges:
        path = '/meta/exchanges'
        return [Exchange(o) for o in self.get(path)]

    def symbol_type_map(self) -> SymbolTypeMap:
        path = '/meta/symbol-types'
        return SymbolTypeMap(self.get(path))

    @deprecated(
        'historic_trades v1 is deprecated and will be removed from the ' +
        'Polygon API in the future. Please upgrade to historic_trades_v2.'
    )
    def historic_trades(self, symbol: str, date, offset=None, limit=None):
        path: str = f'/historic/trades/{symbol}/{date}'
        params = {}
        if offset is not None:
            params['offset'] = offset
        if limit is not None:
            params['limit'] = limit
        raw = self.get(path, params)

        return Trades(raw)

    def historic_trades_v2(self,
                           symbol: str,
                           date: DATE,
                           timestamp: int = None,
                           timestamp_limit: int = None,
                           reverse: bool = None,
                           limit: int = None
                           ) -> TradesV2:
        """
        polygon.io/docs/#get_v2_ticks_stocks_trades__ticker___date__anchor
        :param symbol
        :param date: DATE in this format YYYY-MM-DD
        :param timestamp: timestamp integer
        :param timestamp_limit: timestamp integer. offset, used for pagination.
        :param reverse: bool
        :param limit: max 50000
        :return:
        """
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
    def historic_quotes(self, symbol, date, offset=None, limit=None) -> Quotes:
        path = '/historic/quotes/{}/{}'.format(symbol, date)
        params = {}
        if offset is not None:
            params['offset'] = offset
        if limit is not None:
            params['limit'] = limit
        raw = self.get(path, params)

        return Quotes(raw)

    def historic_quotes_v2(self,
                           symbol: str,
                           date: DATE,
                           timestamp: int = None,
                           timestamp_limit: int = None,
                           reverse: bool = None,
                           limit: int = None
                           ) -> QuotesV2:
        """
        polygon.io/docs/#get_v2_ticks_stocks_nbbo__ticker___date__anchor
        :param symbol
        :param date: DATE in this format YYYY-MM-DD
        :param timestamp: timestamp integer. offset, used for pagination.
        :param timestamp_limit: timestamp integer
        :param reverse: bool
        :param limit: max 50000
        :return:
        """
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

    def historic_agg_v2(self,
                        symbol: str,
                        multiplier: int,
                        timespan: str,
                        _from,
                        to,
                        unadjusted: bool = False,
                        limit: int = None) -> Aggsv2:
        """
        :param symbol:
        :param multiplier: Size of the timespan multiplier (distance between
               samples. e.g if it's 1 we get for daily 2015-01-05, 2015-01-06,
                            2015-01-07, 2015-01-08.
                            if it's 3 we get 2015-01-01, 2015-01-04,
                            2015-01-07, 2015-01-10)
        :param timespan: Size of the time window: minute, hour, day, week,
               month, quarter, year
        :param _from: acceptable types: isoformat string, timestamp int,
        datetime object
        :param to: same
        :param unadjusted
        :param limit: max samples to retrieve
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

    def grouped_daily(self, date, unadjusted: bool = False) -> Aggsv2Set:
        path = f'/aggs/grouped/locale/US/market/STOCKS/{date}'
        params = {'unadjusted': unadjusted}
        raw = self.get(path, params, version='v2')
        return Aggsv2Set(raw)

    def daily_open_close(self, symbol: str, date) -> DailyOpenClose:
        path = f'/open-close/{symbol}/{date}'
        raw = self.get(path)
        return DailyOpenClose(raw)

    def last_trade(self, symbol: str) -> Trade:
        path = '/last/stocks/{}'.format(symbol)
        raw = self.get(path)
        return Trade(raw['last'])

    def last_quote(self, symbol: str) -> Quote:
        path = '/last_quote/stocks/{}'.format(symbol)
        raw = self.get(path)
        # TODO status check
        return Quote(raw['last'])

    def previous_day_bar(self, symbol: str) -> Aggsv2:
        path = '/aggs/ticker/{}/prev'.format(symbol)
        raw = self.get(path, version='v2')
        return Aggsv2(raw)

    def condition_map(self, ticktype='trades') -> ConditionMap:
        path = '/meta/conditions/{}'.format(ticktype)
        return ConditionMap(self.get(path))

    def company(self, symbol: str) -> Company:
        return self._get_symbol(symbol, 'company', Company)

    def _get_symbol(self, symbol: str, resource: str, entity):
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

    def dividends(self, symbol: str) -> Dividends:
        return self._get_symbol(symbol, 'dividends', Dividends)

    def splits(self, symbol: str) -> Splits:
        path = '/meta/symbols/{}/splits'.format(symbol)
        return Splits(self.get(path))

    def earnings(self, symbol: str) -> Earnings:
        return self._get_symbol(symbol, 'earnings', Earnings)

    def financials(self, symbol: str) -> Financials:
        return self._get_symbol(symbol, 'financials', Financials)

    def news(self, symbol: str) -> NewsList:
        path = '/meta/symbols/{}/news'.format(symbol)
        return NewsList(self.get(path))

    def gainers_losers(self, direction: str = "gainers") -> Tickers:
        path = '/snapshot/locale/us/markets/stocks/{}'.format(direction)
        return [
            Ticker(ticker) for ticker in
            self.get(path, version='v2')['tickers']
        ]

    def all_tickers(self) -> Tickers:
        path = '/snapshot/locale/us/markets/stocks/tickers'
        return [
            Ticker(ticker) for ticker in
            self.get(path, version='v2')['tickers']
        ]

    def snapshot(self, symbol: str) -> Ticker:
        path = '/snapshot/locale/us/markets/stocks/tickers/{}'.format(symbol)
        return Ticker(self.get(path, version='v2'))
