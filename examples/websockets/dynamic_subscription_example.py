"""
In this example code we will show a pattern that allows a user to change
the websocket subscriptions as they please.
"""
import logging
import threading
import asyncio
import time
from alpaca_trade_api.stream import Stream
from alpaca_trade_api.common import URL

ALPACA_API_KEY = "<YOUR-API-KEY>"
ALPACA_SECRET_KEY = "<YOUR-SECRET-KEY>"


async def print_trade(t):
    print('trade', t)


async def print_quote(q):
    print('quote', q)


async def print_bar(bar):
    print('bar', bar)

PREVIOUS = None


def consumer_thread():
    global conn
    conn = Stream(ALPACA_API_KEY,
                  ALPACA_SECRET_KEY,
                  base_url=URL('https://paper-api.alpaca.markets'),
                  data_feed='iex')

    conn.subscribe_quotes(print_quote, 'AAPL')
    global PREVIOUS
    PREVIOUS = "AAPL"
    conn.run()

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s',
                        level=logging.INFO)
    threading.Thread(target=consumer_thread).start()
    time.sleep(5)  # give the initial connection time to be established
    subscriptions = {"BABA": print_quote,
                     "AAPL": print_quote,
                     "TSLA": print_quote,
                     }

    while 1:
        for ticker, handler in subscriptions.items():
            conn.unsubscribe_quotes(PREVIOUS)
            conn.subscribe_quotes(handler, ticker)
            PREVIOUS = ticker
            time.sleep(20)
