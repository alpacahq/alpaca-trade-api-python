"""
In this example code we wrap the ws connection to make sure we reconnect
in case of ws disconnection.
"""

import logging
import time
from alpaca_trade_api import StreamConn
from alpaca_trade_api.common import URL

logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)

ALPACA_API_KEY = "<YOUR-API-KEY>"
ALPACA_SECRET_KEY = "<YOUR-SECRET-KEY>"
USE_POLYGON = False


def run_connection(conn, channels):
    try:
        conn.run(channels)
    except Exception as e:
        print(f'Exception from websocket connection: {e}')
    finally:
        print("Trying to re-establish connection")
        time.sleep(3)
        run_connection(conn, channels)

if __name__ == '__main__':
    channels = ['alpacadatav1/Q.GOOG']

    conn = StreamConn(
        ALPACA_API_KEY,
        ALPACA_SECRET_KEY,
        base_url=URL('https://paper-api.alpaca.markets'),
        data_url=URL('https://data.alpaca.markets'),
        # data_url=URL('http://127.0.0.1:8765'),
        data_stream='polygon' if USE_POLYGON else 'alpacadatav1'
    )


    @conn.on(r'^AM\..+$')
    async def on_minute_bars(conn, channel, bar):
        print('bars', bar)


    @conn.on(r'Q\..+')
    async def on_quotes(conn, channel, quote):
        print('quote', quote)


    @conn.on(r'T\..+')
    async def on_trades(conn, channel, trade):
        print('trade', trade)

    run_connection(conn, channels)