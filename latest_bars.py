from alpaca_trade_api.rest import REST

def print_bars(bars, name):
    print(f"Printing bars for {name}")
    print(bars)
    # for bar in bars[:2]:
    #     print(bar)
    print()

client = REST()

c_symbol = ["BTC/USD", "LTC/USD"]

latest_c_bar = client.get_latest_crypto_quotes(
    symbols=c_symbol,
)
print_bars(latest_c_bar, name="multi crypto bars")

c_symbol = ["BTC/USD"]

latest_c_bar = client.get_latest_crypto_quotes(
    symbols=c_symbol,
)
print_bars(latest_c_bar, name="multi crypto bars 2")

"""
Mine:
https://data.alpaca.markets/v1beta2/crypto/latest/bars?exchange=CBSE&symbols=BTC%2FUSD

Theirs:
https://data.alpaca.markets/v1beta2/crypto/latest/bars?symbols=BTC/USD,LTC/USD'

"""