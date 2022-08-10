from alpaca_trade_api.rest import REST

def print_bars(bars, name):
    print(f"Printing bars for {name}")
    print(bars)
    # for bar in bars[:2]:
    #     print(bar)
    print()

client = REST()

c_symbol = ["BTC/USD"]
mc_symbol = ["BTC/USD", "LTC/USD"]
s_symbol = "AAPL"
ms_symbol = ["AAPL", "GME"]

timeframe = "1Day"
start = "2022-01-03T00:00:00Z"
end = "2022-01-04T00:00:00Z"
limit = 3

multi_c_bars = client.get_crypto_bars(
    symbol=mc_symbol,
    timeframe=timeframe,
    start=start,
    end=end,
    limit=limit,
)
print_bars(multi_c_bars, name="multi crypto bars")

c_bars = client.get_crypto_bars(
    symbol=c_symbol,
    timeframe=timeframe,
    start=start,
    end=end,
    limit=limit,
)
print_bars(c_bars, name="singular crypto bars")

s_bars = client.get_bars(
    symbol=s_symbol,
    timeframe=timeframe,
    start=start,
    end=end,
    limit=limit,
)
print_bars(s_bars, name="singular stock bars")

ms_bars = client.get_bars(
    symbol=ms_symbol,
    timeframe=timeframe,
    start=start,
    end=end,
    limit=limit,
)
print_bars(s_bars, name="multi stock bars")