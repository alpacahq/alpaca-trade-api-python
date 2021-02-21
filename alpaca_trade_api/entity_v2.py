from .entity import Entity, _NanoTimestamped

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


class Trade(_NanoTimestamped, Entity):
    pass


class Quote(_NanoTimestamped, Entity):
    pass


class Bar(_NanoTimestamped, Entity):
    pass
