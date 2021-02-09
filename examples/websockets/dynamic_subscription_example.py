"""
In this example code we will show a pattern that allows a user to change
the websocket subscriptions as they please.
"""
import logging
import threading
import asyncio
import time
from alpaca_trade_api import StreamConn
from alpaca_trade_api.common import URL

ALPACA_API_KEY = "<YOUR-API-KEY>"
ALPACA_SECRET_KEY = "<YOUR-SECRET-KEY>"
USE_POLYGON = False

conn: StreamConn = None

def consumer_thread():

    try:
        # make sure we have an event loop, if not create a new one
        loop = asyncio.get_event_loop()
        loop.set_debug(True)
    except RuntimeError:
        asyncio.set_event_loop(asyncio.new_event_loop())

    global conn
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

    conn.run(['alpacadatav1/Q.GOOG'])

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)
    threading.Thread(target=consumer_thread).start()

    loop = asyncio.get_event_loop()

    time.sleep(5)  # give the initial connection time to be established
    subscriptions = [['alpacadatav1/AM.TSLA'], ['alpacadatav1/Q.GOOG'],
                     ['alpacadatav1/T.AAPL']]

    while 1:
        for channels in subscriptions:
            loop.run_until_complete(conn.subscribe(channels))
            if "AM." in channels[0]:
                time.sleep(60)  # aggs are once every minute. give it time
            else:
                time.sleep(20)
