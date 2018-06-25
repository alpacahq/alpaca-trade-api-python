import pandas as pd
import pprint
import re

ISO8601YMD = re.compile(r'\d{4}-\d{2}-\d{2}T')


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
        return getattr(super(), key)

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
    pass


class AssetBars(Entity):

    @property
    def df(self):
        if not hasattr(self, '_df'):
            df = pd.DataFrame(self._raw['bars'])
            if len(df.columns) == 0:
                df.columns = ('time', 'open', 'high', 'low', 'close', 'volume')
            df = df.set_index('time')
            df.index = pd.to_datetime(df.index)
            self._df = df
        return self._df

    @property
    def bars(self):
        if not hasattr(self, '_bars'):
            raw = self._raw
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
            self._bars = bars
        return self._bars


class Quote(Entity):
    pass


class Fundamental(Entity):
    pass


class Clock(Entity):
    def __getattr__(self, key):
        if key in self._raw:
            val = self._raw[key]
            if key in ('timestamp', 'next_open', 'next_close'):
                return pd.Timestamp(val)
            else:
                return val
        return getattr(super(), key)


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
        return getattr(super(), key)
