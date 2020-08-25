from alpaca_trade_api import StreamConn
from alpaca_trade_api.common import URL


ALPACA_API_KEY = "<YOUR-API-KEY>"
ALPACA_SECRET_KEY = "<YOUR-SECRET-KEY>"
USE_POLYGON = False


if __name__ == '__main__':
    import logging

    logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)
    conn = StreamConn(
            ALPACA_API_KEY,
            ALPACA_SECRET_KEY,
            base_url=URL('https://paper-api.alpaca.markets'),
            data_url=URL('https://data.alpaca.markets'),
            # data_url=URL('ws://127.0.0.1:8765'),
            data_stream='polygon' if USE_POLYGON else 'alpacadatav1'
        )

    @conn.on(r'^trade_updates$')
    async def on_account_updates(conn, channel, account):
        print('account', account)

    @conn.on(r'^status$')
    async def on_status(conn, channel, data):
        print('polygon status update', data)

    @conn.on(r'^AM\..+$')
    async def on_minute_bars(conn, channel, bar):
        print('bars', bar)

    @conn.on(r'^AM*$')
    async def on_minute_bars(conn, channel, bar):
        print('bars', bar)

    quote_count = 0  # don't print too much quotes
    @conn.on(r'Q\..+', ['AAPL'])
    async def on_minute_bars(conn, channel, bar):
        global quote_count
        if quote_count % 10 == 0:
            print('bars', bar)
        quote_count += 1

    @conn.on(r'^A*$')
    async def on_second_bars(conn, channel, bar):
        print('bars', bar)

    # blocks forever
    # conn.run(['trade_updates', 'AM.*', 'alpacadatav1/Q.AAPL'])
    # conn.run(['trade_updates', 'AM.*'])
    # conn.run(['trade_updates', 'AM.AAPL'])
    conn.run(['trade_updates', 'alpacadatav1/AM.AAPL'])
