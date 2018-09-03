import pandas as pd
import pprint

NY = 'America/New_York'


class Entity(object):
    def __init__(self, raw):
        self._raw = raw

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
            Agg(rename_keys(tick, raw['map']))
            for tick in raw['ticks']
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
            df = pd.DataFrame(
                sorted(raw['ticks'], key=lambda d: d['d']),
                columns=('o', 'h', 'l', 'c', 'v', 'd'),
            )
            df.columns = [raw['map'][c] for c in df.columns]
            if size[0] == 'm':
                df.set_index('timestamp', inplace=True)
                # astype is necessary to deal with empty result
                df.index = pd.to_datetime(
                    df.index.astype('int64') * 1000000,
                    utc=True,
                ).tz_convert(NY)
            else:
                df.set_index('day', inplace=True)
                df.index = pd.to_datetime(
                    df.index).tz_localize(NY)

            df.sort_index(inplace=True)
            self._df = df

        return self._df


class _TradeOrQuote(object):
    '''Mixin for Trade and Quote'''

    def __getattr__(self, key):
        if key in self._raw:
            val = self._raw[key]
            if key == 'timestamp':
                return pd.Timestamp(val, tz=NY, unit='ms')
            return val
        return getattr(super(), key)


class _TradesOrQuotes(object):
    '''Mixin for Trades and Quotes'''

    def __init__(self, raw):
        def rename_keys(tick, map):
            return {
                map[k]: v for k, v in tick.items()
            }

        unit_class = self.__class__._unit
        super().__init__([
            unit_class(rename_keys(tick, raw['map']))
            for tick in raw['ticks']
        ])
        self._raw = raw

    @property
    def df(self):
        if not hasattr(self, '_df'):
            raw = self._raw
            columns = self.__class__._columns
            df = pd.DataFrame(
                sorted(raw['ticks'], key=lambda d: d['t']),
                columns=columns,
            )
            df.columns = [raw['map'][c] for c in df.columns]
            df.set_index('timestamp', inplace=True)
            df.index = pd.to_datetime(
                df.index.astype('int64') * 1000000,
                utc=True,
            ).tz_convert(NY)

            df.sort_index(inplace=True)
            self._df = df

        return self._df


class Trade(_TradeOrQuote, Entity):
    pass


class Trades(_TradesOrQuotes, list):
    _columns = ('p', 's', 'e', 't', 'c1', 'c2', 'c3', 'c4')
    _unit = Trade


class Quote(_TradeOrQuote, Entity):
    pass


class Quotes(_TradesOrQuotes, list):
    _columns = ('t', 'c', 'bE', 'aE', 'aP', 'bP', 'bS', 'aS')
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
