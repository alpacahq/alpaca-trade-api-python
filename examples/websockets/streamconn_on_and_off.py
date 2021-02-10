"""
In this example code we will show how to shut the streamconn websocket
connection down and then up again. it's the ability to stop/start the
connection
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

    loop = asyncio.get_event_loop()

    while 1:
        threading.Thread(target=consumer_thread).start()
        time.sleep(5)
        loop.run_until_complete(conn.stop_ws())
        time.sleep(20)
