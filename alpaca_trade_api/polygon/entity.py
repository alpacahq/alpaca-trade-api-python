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
        lkey = key.lower()
        if lkey in ((
            'open', 'low', 'high', 'close',
            'volume')):
            key = lkey[0]
        elif lkey == 'timestamp' or lkey == 'day':
            key = 'd'
        if key in self._raw:
            val = self._raw[key]
            if key == 'd':
                if isinstance(val, str):
                    return pd.Timestamp(val, tz=NY)
                return pd.Timestamp(
                    val, unit='ms', tz=NY)
            return val
        return getattr(super(), key)


class Aggs(list):
    def __init__(self, raw):
        super().__init__([
            Agg(tick) for tick in raw['ticks']
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
                    df.index, utc=True,
                ).tz_convert(NY)
            self._df = df

        return self._df


class Trade(Entity):
    pass


class Quote(Entity):
    pass

class Quotes(list):
    def __init__(self, raw):
        pass