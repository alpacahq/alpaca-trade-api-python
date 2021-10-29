"""
In this example code we wrap the ws connection to make sure we reconnect
in case of ws disconnection.
"""

import logging
import time
from alpaca_trade_api.stream import Stream
from alpaca_trade_api.common import URL

logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)

ALPACA_API_KEY = "<YOUR-API-KEY>"
ALPACA_SECRET_KEY = "<YOUR-SECRET-KEY>"


def run_connection(conn):
    try:
        conn.run()
    except KeyboardInterrupt:
        print("Interrupted execution by user")
        loop.run_until_complete(conn.stop_ws())
        exit(0)
    except Exception as e:
        print(f'Exception from websocket connection: {e}')
    finally:
        print("Trying to re-establish connection")
        time.sleep(3)
        run_connection(conn)


async def print_quote(q):
    print('quote', q)


if __name__ == '__main__':
    conn = Stream(ALPACA_API_KEY,
                  ALPACA_SECRET_KEY,
                  base_url=URL('https://paper-api.alpaca.markets'),
                  data_feed='iex')

    conn.subscribe_quotes(print_quote, 'AAPL')

    run_connection(conn)
