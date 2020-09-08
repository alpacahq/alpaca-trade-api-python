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
            data_stream='polygon' if USE_POLYGON else 'alpacadatav1'
        )
    if USE_POLYGON:
        @conn.on(r'^status$')
        async def on_status(conn, channel, data):
            print('polygon status update', data)

        @conn.on(r'^A*$')
        async def on_second_bars(conn, channel, bar):
            print('bars', bar)

    @conn.on(r'^AM\..+$')
    async def on_minute_bars(conn, channel, bar):
        print('bars', bar)

    quote_count = 0  # don't print too much quotes
    @conn.on(r'Q\..+', ['AAPL'])
    async def on_quotes(conn, channel, quote):
        global quote_count
        if quote_count % 10 == 0:
            print('bars', quote)
        quote_count += 1


    @conn.on(r'T\..+', ['AAPL'])
    async def on_trades(conn, channel, trade):
        print('trade', trade)


    if USE_POLYGON:
        conn.run(['trade_updates', 'AM.AAPL'])
    else:
        conn.run(['trade_updates', 'alpacadatav1/AM.AAPL'])
