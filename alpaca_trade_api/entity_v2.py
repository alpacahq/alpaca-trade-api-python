from enum import Enum
import pandas as pd
from .entity import Bar, Trade, Quote


trade_mapping_v2 = {
    "i": "id",
    "S": "symbol",
    "c": "conditions",
    "x": "exchange",
    "p": "price",
    "s": "size",
    "t": "timestamp",
    "z": "tape"
}

quote_mapping_v2 = {
    "S": "symbol",
    "ax": "ask_exchange",
    "ap": "ask_price",
    "as": "ask_size",
    "bx": "bid_exchange",
    "bp": "bid_price",
    "bs": "bid_size",
    "c": "conditions",
    "t": "timestamp",
    "z": "tape"
}

bar_mapping_v2 = {
    "S": "symbol",
    "o": "open",
    "h": "high",
    "l": "low",
    "c": "close",
    "v": "volume",
    "t": "timestamp"
}


class EntityListType(Enum):
    Trade = Trade, trade_mapping_v2
    Quote = Quote, quote_mapping_v2
    Bar = Bar, bar_mapping_v2


class EntityList(list):
    def __init__(self, entity_type: EntityListType, raw):
        entity = entity_type.value[0]
        super().__init__([entity(o) for o in raw])
        self._raw = raw
        self.mapping = entity_type.value[1]

    @property
    def df(self):
        if not hasattr(self, '_df'):
            df = pd.DataFrame(
                self._raw,
            )

            df.columns = [self.mapping[c] for c in df.columns]
            if not df.empty:
                df.set_index('timestamp', inplace=True)
                df.index = pd.DatetimeIndex(df.index)
            self._df = df
        return self._df


class BarsV2(EntityList):
    def __init__(self, raw):
        super().__init__(EntityListType.Bar, raw)


class TradesV2(EntityList):
    def __init__(self, raw):
        super().__init__(EntityListType.Trade, raw)


class QuotesV2(EntityList):
    def __init__(self, raw):
        super().__init__(EntityListType.Quote, raw)
