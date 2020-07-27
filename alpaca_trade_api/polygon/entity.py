import pandas as pd
import pprint

NY = 'America/New_York'


class Entity(object):
    def __init__(self, raw):
        self._raw = raw
        if 'from' in self._raw:
            # can't use python keyword 'from'. if the api returns it,
            # we switch it to _from, which is usable for the users.
            self._raw['_from'] = self._raw['from']

    def __getattr__(self, key):
        if key in self._raw:
            val = self._raw[key]
            return val
        return getattr(super(), key)

    def __repr__(self):
        return '{name}({raw})'.format(
            name=self.__class__.__name__,
            raw=pprint.pformat(self._raw, indent=4),
        )


class Agg(Entity):
    def __getattr__(self, key):
        if key in self._raw:
            val = self._raw[key]
            if key == 'day':
                return pd.Timestamp(val, tz=NY)
            elif key in ('timestamp', 'start', 'end'):
                return pd.Timestamp(val, tz=NY, unit='ms')
            return val
        return getattr(super(), key)


class Aggs(list):
    def __init__(self, raw):
        def rename_keys(tick, map):
            return {
                map[k]: v for k, v in tick.items()
            }

        super().__init__([
            Agg(rename_keys(tick, raw['map'])) for tick in raw['ticks']
        ])
        self._raw = raw

    @property
    def df(self):
        if not hasattr(self, '_df'):
            raw = self._raw
            size = raw['aggType']
            # polygon doesn't return in ascending order
            # Do not rely on df.sort_values() as this library
            # may be used with older pandas
            keycol = 't' if size[0] == 'm' else 'd'
            columns = ('o', 'h', 'l', 'c', 'v', keycol)
            df = pd.DataFrame(
                sorted(raw['ticks'], key=lambda d: d[keycol]),
                columns=columns,
            )
            df.columns = [raw['map'][c] for c in df.columns]
            if size[0] == 'm':
                df.set_index('timestamp', inplace=True)
                # astype is necessary to deal with empty result
                df.index = pd.to_datetime(
                    df.index.astype('int64'),
                    unit='ms',
                    utc=True,
                ).tz_convert(NY)
            else:
                df.set_index('day', inplace=True)
                df.index = pd.to_datetime(
                    df.index).tz_localize(NY)

            df.sort_index(inplace=True)
            self._df = df

        return self._df


class Aggsv2(list):

    def __init__(self, raw):

        self._raw = raw
        super().__init__([
            Agg(tick) for tick in self.rename_keys()
        ])

    def _raw_results(self):
        results = self._raw.get('results')
        if not results:
            # this is not very pythonic but it's written like this because
            # the raw response for empty aggs was None, and this:
            # self._raw.get('results', []) returns None, not [] which breaks
            # when we try to iterate it.
            return []
        return results

    def rename_keys(self):
        colmap = {
            "o": "open",
            "h": "high",
            "l": "low",
            "c": "close",
            "v": "volume",
            "t": "timestamp",
            "vw": "vwap",
        }

        return [
            {colmap.get(k, k): v for k, v in tick.items()}
            for tick in self._raw_results()
        ]

    @property
    def df(self):
        if not hasattr(self, '_df'):
            columns = ('timestamp', 'open', 'high', 'low', 'close',
                       'volume', 'vwap')
            df = pd.DataFrame(
                self.rename_keys(),
                columns=columns
            )
            df.set_index('timestamp', inplace=True)
            df.index = pd.to_datetime(
                df.index.astype('int64'),
                unit='ms', utc=True
            ).tz_convert(NY)

            self._df = df

        return self._df


class Aggsv2Set(dict):
    def __init__(self, raw):
        ticker_ticks = {}
        for tick in raw['results']:
            if ticker_ticks.get(tick['T']):
                ticker_ticks[tick['T']].append(tick)
            else:
                ticker_ticks[tick['T']] = [tick]
        super().__init__({
            ticker: Aggsv2({'results': ticks})
            for ticker, ticks in ticker_ticks.items()
        })


class _TradeOrQuote(object):
    '''Mixin for Trade and Quote'''

    def __getattr__(self, key):
        if key in self._raw:
            val = self._raw[key]
            if key == 'timestamp':
                return pd.Timestamp(val, tz=NY, unit='ms')
            elif key in [
                'sip_timestamp', 'participant_timestamp', 'trf_timestamp'
            ]:
                return pd.Timestamp(val, tz=NY, unit='ns')
            return val
        return getattr(super(), key)


class _TradesOrQuotes(object):
    '''Mixin for Trades and Quotes'''

    def __init__(self, raw):
        def rename_keys(tick, map):
            if type(map['t']) is dict:
                # Must be a v2 response
                return {
                    map[k]['name']: v for k, v in tick.items()
                }
            return {
                map[k]: v for k, v in tick.items()
            }

        unit_class = self.__class__._unit
        results = {}
        if 'ticks' in raw:
            results = raw['ticks']
        else:
            results = raw['results']
        super().__init__([
            unit_class(rename_keys(result, raw['map']))
            for result in results
        ])
        self._raw = raw

    @property
    def df(self):
        if not hasattr(self, '_df'):
            raw = self._raw
            columns = self.__class__._columns
            results = {}
            if 'ticks' in raw:
                results = raw['ticks']
            else:
                results = raw['results']
            df = pd.DataFrame(
                sorted(results, key=lambda d: d['t']),
                columns=columns,
            )
            if type(raw['map']['t']) is dict:
                # Must be v2 response
                df.columns = [raw['map'][c]['name'] for c in df.columns]
                df.set_index('sip_timestamp', inplace=True)
                df.index = pd.to_datetime(
                    df.index.astype('int64'),
                    utc=True,
                    unit='ns',
                ).tz_convert(NY)
            else:
                df.columns = [raw['map'][c] for c in df.columns]
                df.set_index('timestamp', inplace=True)
                df.index = pd.to_datetime(
                    df.index.astype('int64'),
                    utc=True,
                    unit='ms',
                ).tz_convert(NY)

            df.sort_index(inplace=True)
            self._df = df

        return self._df


class Trade(_TradeOrQuote, Entity):
    pass


class Trades(_TradesOrQuotes, list):
    _columns = ('p', 's', 'e', 't', 'c1', 'c2', 'c3', 'c4')
    _unit = Trade


class TradesV2(_TradesOrQuotes, list):
    _columns = ('t', 'y', 'f', 'q', 'i', 'x', 's', 'c', 'p', 'z')
    _unit = Trade


class Quote(_TradeOrQuote, Entity):
    pass


class Quotes(_TradesOrQuotes, list):
    _columns = ('t', 'c', 'bE', 'aE', 'aP', 'bP', 'bS', 'aS')
    _unit = Quote


class QuotesV2(_TradesOrQuotes, list):
    _columns = ('t', 'y', 'f', 'q', 'c', 'i', 'p', 'x', 's', 'P', 'X',
                'S', 'z')
    _unit = Quote


class Exchange(Entity):
    pass


class SymbolTypeMap(Entity):
    pass


class ConditionMap(Entity):
    pass


class Company(Entity):
    pass


class EntityList(list):
    def __init__(self, raw):
        super().__init__([
            self._entity_class(o) for o in raw
        ])
        self._raw = raw


class Dividend(Entity):
    pass


class Dividends(EntityList):
    _entity_class = Dividend


class Split(Entity):
    pass


class Splits(EntityList):
    _entity_class = Split


class Earning(Entity):
    pass


class Earnings(EntityList):
    _entity_class = Earning


class Financial(Entity):
    pass


class Financials(EntityList):
    _entity_class = Financial


class News(Entity):
    pass


class NewsList(EntityList):
    _entity_class = News


class Ticker(Entity):
    pass


class Symbol(Entity):
    pass


class DailyOpenClose(Entity):
    pass


trade_mapping = {
    "sym": "symbol",
    "c": "conditions",
    "x": "exchange",
    "p": "price",
    "s": "size",
    "t": "timestamp"
}

quote_mapping = {
    "sym": "symbol",
    "ax": "askexchange",
    "ap": "askprice",
    "as": "asksize",
    "bx": "bidexchange",
    "bp": "bidprice",
    "bs": "bidsize",
    "c": "condition",
    "t": "timestamp"
}

agg_mapping = {
    "sym": "symbol",
    "o": "open",
    "c": "close",
    "h": "high",
    "l": "low",
    "a": "average",
    "x": "exchange",
    "v": "volume",
    "s": "start",
    "e": "end",
    "vw": "vwap",
    "av": "totalvolume",
}
