import pandas as pd
import pprint
import re

ISO8601YMD = re.compile(r'\d{4}-\d{2}-\d{2}T')
NY = 'America/New_York'


class Entity(object):
    '''This helper class provides property access (the "dot notation")
    to the json object, backed by the original object stored in the _raw
    field.
    '''

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
                return pd.Timestamp(val)
            else:
                return val
        return super().__getattribute__(key)

    def __repr__(self):
        return '{name}({raw})'.format(
            name=self.__class__.__name__,
            raw=pprint.pformat(self._raw, indent=4),
        )


class Account(Entity):
    pass


class Asset(Entity):
    pass


class Order(Entity):
    pass


class Position(Entity):
    pass


class Bar(Entity):
    def __getattr__(self, key):
        if key == 't':
            val = self._raw[key[0]]
            return pd.Timestamp(val, unit='s', tz=NY)
        return super().__getattr__(key)


class Bars(list):
    def __init__(self, raw):
        super().__init__([Bar(o) for o in raw])
        self._raw = raw

    @property
    def df(self):
        if not hasattr(self, '_df'):
            df = pd.DataFrame(
                self._raw, columns=('t', 'o', 'h', 'l', 'c', 'v'),
            )
            alias = {
                't': 'time',
                'o': 'open',
                'h': 'high',
                'l': 'low',
                'c': 'close',
                'v': 'volume',
            }
            df.columns = [alias[c] for c in df.columns]
            df.set_index('time', inplace=True)
            df.index = pd.to_datetime(
                df.index * 1e9, utc=True,
            ).tz_convert(NY)
            self._df = df
        return self._df


class BarSet(dict):
    def __init__(self, raw):
        for symbol in raw:
            self[symbol] = Bars(raw[symbol])
        self._raw = raw

    @property
    def df(self):
        '''## Experimental '''
        if not hasattr(self, '_df'):
            dfs = []
            for symbol, bars in self.items():
                df = bars.df.copy()
                df.columns = pd.MultiIndex.from_product(
                    [[symbol, ], df.columns])
                dfs.append(df)
            if len(dfs) == 0:
                self._df = pd.DataFrame()
            else:
                self._df = pd.concat(dfs, axis=1)
        return self._df


class Clock(Entity):
    def __getattr__(self, key):
        if key in self._raw:
            val = self._raw[key]
            if key in ('timestamp', 'next_open', 'next_close'):
                return pd.Timestamp(val)
            else:
                return val
        return super().__getattr__(key)


class Calendar(Entity):
    def __getattr__(self, key):
        if key in self._raw:
            val = self._raw[key]
            if key in ('date',):
                return pd.Timestamp(val)
            elif key in ('open', 'close'):
                return pd.Timestamp(val).time()
            else:
                return val
        return super().__getattr__(key)
