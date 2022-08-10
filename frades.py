from alpaca_trade_api.rest import REST

def print_trades(trades, name):
    print(f"Printing snapshots for {name}")
    print(trades)
    print(trades["BTC/USD"])
    print()

client = REST()

mc_symbol = ["BTC/USD", "LTC/USD"]
c_symbol = ["LTC/USD"]

latest_c_bar = client.get_latest_crypto_orderbooks(
    symbols=mc_symbol,
)
print_trades(latest_c_bar, name="multi crypto orderbooks")

c_symbol = ["BTC/USD"]

latest_c_bar = client.get_latest_crypto_orderbooks(
    symbols=c_symbol,
)
print_trades(latest_c_bar, name="single crypto orderbooks")