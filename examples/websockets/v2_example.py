import logging

from alpaca_trade_api.stream import Stream

# Uncomment URL import to test with paper credentials
# from alpaca_trade_api.common import URL

log = logging.getLogger(__name__)


async def print_trade(t):
    print('trade', t)


async def print_quote(q):
    print('quote', q)


async def print_trade_update(tu):
    print('trade update', tu)


def main():
    logging.basicConfig(level=logging.INFO)
    feed = 'iex'  # <- replace to SIP if you have PRO subscription
    
    stream = Stream(data_feed=feed, raw_data=True)  # <- add base_url=URL('https://paper-api.alpaca.markets') for paper
    stream.subscribe_trade_updates(print_trade_update)
    stream.subscribe_trades(print_trade, 'AAPL')
    stream.subscribe_quotes(print_quote, 'IBM')

    @stream.on_bar('MSFT')
    async def _(bar):
        print('bar', bar)

    stream.run()


if __name__ == "__main__":
    main()
