"""
In this example code we will show how to shut the streamconn websocket
connection down and then up again. it's the ability to stop/start the
connection
"""
import logging
import threading
import asyncio
import time
from concurrent.futures import ThreadPoolExecutor
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


def consumer_thread():
    try:
        # make sure we have an event loop, if not create a new one
        loop = asyncio.get_event_loop()
        loop.set_debug(True)
    except RuntimeError:
        asyncio.set_event_loop(asyncio.new_event_loop())

    global conn
    conn = Stream(ALPACA_API_KEY,
                  ALPACA_SECRET_KEY,
                  base_url=URL('https://paper-api.alpaca.markets'),
                  data_feed='iex')

    conn.subscribe_quotes(print_quote, 'AAPL')
    conn.run()


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s  %(levelname)s %(message)s',
                        level=logging.INFO)

    loop = asyncio.get_event_loop()
    pool = ThreadPoolExecutor(1)

    while 1:
        try:
            pool.submit(consumer_thread)
            time.sleep(20)
            loop.run_until_complete(conn.stop_ws())
            time.sleep(20)
        except KeyboardInterrupt:
            print("Interrupted execution by user")
            loop.run_until_complete(conn.stop_ws())
            exit(0)
        except Exception as e:
            print("You goe an exception: {} during execution. continue "
                  "execution.".format(e))
            # let the execution continue
            pass
