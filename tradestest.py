from alpaca_trade_api.rest import REST

def print_trades(trades, name):
    print(f"Printing trades for {name}")
    print(trades)
    # for bar in bars[:2]:
    #     print(bar)
    print()

client = REST()

c_symbol = ["BTC/USD"]
mc_symbol = ["BTC/USD", "LTC/USD"]
s_symbol = "AAPL"
ms_symbol = ["AAPL", "GME"]

start = "2022-01-03T00:00:00Z"
end = "2022-01-04T00:00:00Z"
limit = 3

multi_c_trades = client.get_crypto_quotes(
    symbol=mc_symbol,
    start=start,
    end=end,
    limit=limit,
)
print_trades(multi_c_trades, name="multi crypto trades")

c_trades = client.get_crypto_quotes(
    symbol=c_symbol,
    start=start,
    end=end,
    limit=limit,
)
print_trades(c_trades, name="singular crypto trades")

# multi_trades = client.get_trades(
#     symbol=ms_symbol,
#     start=start,
#     end=end,
#     limit=limit,
# )
# print_trades(multi_trades, name="multi trades")

# trades = client.get_trades(
#     symbol=s_symbol,
#     start=start,
#     end=end,
#     limit=limit,
# )
# print_trades(trades, name="singular trades")