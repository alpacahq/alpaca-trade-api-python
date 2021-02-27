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

        sec_agg_count = 0  # don't print too much quotes
        @conn.on(r'A.*')
        async def on_agg_sec(conn, channel, bars):
            global sec_agg_count
            if sec_agg_count % 1000 == 0:
                print('sec bars', bars)
            sec_agg_count += 1

        quote_count = 0  # don't print too much quotes
        @conn.on(r'Q.*')
        async def on_quotes(conn, channel, quote):
            global quote_count
            if quote_count % 1000 == 0:
                print('quote', quote)
            quote_count += 1

        agg_count = 0  # don't print too much quotes
        @conn.on(r'AM.*')
        async def on_agg_min(conn, channel, bars):
            global agg_count
            if agg_count % 1000 == 0:
                print('bars', bars)
            agg_count += 1

        trade_count = 0  # don't print too much quotes
        @conn.on(r'T.*')
        async def on_trades(conn, channel, trade):
            global trade_count
            if trade_count % 1000 == 0:
                print('trade', trade)
            trade_count += 1

    else:
        @conn.on(r'^AM\..+$')
        async def on_minute_bars(conn, channel, bar):
            print('bars', bar)

        quote_count = 0  # don't print too much quotes
        @conn.on(r'Q\..+')
        async def on_quotes(conn, channel, quote):
            global quote_count
            if quote_count % 10 == 0:
                print('quote', quote)
            quote_count += 1

        @conn.on(r'T\..+')
        async def on_trades(conn, channel, trade):
            print('trade', trade)


    if USE_POLYGON:
        # you could use either one of these:
        # conn.run(['trade_updates', 'AM.AAPL', 'Q.AA', 'T.*'])
        # conn.run(['trade_updates', 'AM.AAPL', 'Q.AA', 'T.*'])
        # conn.run(['AM.*', 'A.*', 'Q.*', 'T.*'])
        # conn.run(['trade_updates', 'Q.*', 'T.*'])
        # conn.run(['trade_updates', 'AM.*', 'A.*'])
        conn.run(['Q.AAPL'])
    else:
        # these won't work:
        # conn.run(['T.*'])
        # conn.run(['Q.*'])
        # conn.run(['alpacadatav1/Q.*'])
        # conn.run(['T.TSLA'])
        # conn.run(['Q.TSLA'])

        # these are fine:
        # conn.run(['AM.*'])
        # conn.run(['alpacadatav1/AM.*'])

        # conn.run(['alpacadatav1/AM.TSLA'])
        # conn.run(['alpacadatav1/Q.GOOG'])
        # conn.run(['trade_updates', 'alpacadatav1/Q.GOOG', 'alpacadatav1/AM.TSLA'])
        conn.run(['alpacadatav1/T.TSLA'])

