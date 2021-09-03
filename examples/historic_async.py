import sys
import asyncio
import alpaca_trade_api as tradeapi
from alpaca_trade_api.rest import TimeFrame, URL
from alpaca_trade_api.rest_async import gather_with_concurrency, AsyncRest
import pandas as pd

NY = 'America/New_York'


async def get_historic_bars(symbols, start, end, timeframe: TimeFrame):
    major = sys.version_info.major
    minor = sys.version_info.minor
    if major < 3 or minor < 6:
        raise Exception('asyncio is not support in your python version')
    print(f"Getting data for {len(symbols)} symbols, timeframe: {timeframe},"
          f" between dates: start={start}, end={end}")

    tasks = []

    for symbol in symbols:
        tasks.append(
            rest.get_bars_async(symbol, start, end, timeframe, limit=500))
    if minor >= 8:
        results = await asyncio.gather(*tasks)
    else:
        results = await gather_with_concurrency(500, *tasks)

    bad_requests = 0
    for response in results:
        if not len(response[1]):
            bad_requests += 1

    print(f"Total of {len(results)} Bars, and {bad_requests} empty responses.")


async def get_historic_trades(symbols, start, end, timeframe: TimeFrame):
    major = sys.version_info.major
    minor = sys.version_info.minor
    if major < 3 or minor < 6:
        raise Exception('asyncio is not support in your python version')
    print(f"Getting data for {len(symbols)} symbols, timeframe: {timeframe},"
          f" between dates: start={start}, end={end}")

    tasks = []

    for symbol in symbols:
        tasks.append(
            rest.get_trades_async(symbol, start, end, timeframe, limit=500))
    if minor >= 8:
        results = await asyncio.gather(*tasks)
    else:
        results = await gather_with_concurrency(500, *tasks)

    bad_requests = 0
    for response in results:
        if not len(response[1]):
            bad_requests += 1

    print(
        f"Total of {len(results)} Trades, and {bad_requests} empty responses.")


async def get_historic_quotes(symbols, start, end, timeframe: TimeFrame):
    major = sys.version_info.major
    minor = sys.version_info.minor
    if major < 3 or minor < 6:
        raise Exception('asyncio is not support in your python version')
    print(f"Getting data for {len(symbols)} symbols, timeframe: {timeframe},"
          f" between dates: start={start}, end={end}")

    tasks = []

    for symbol in symbols:
        tasks.append(
            rest.get_quotes_async(symbol, start, end, timeframe, limit=500))
    if minor >= 8:
        results = await asyncio.gather(*tasks)
    else:
        results = await gather_with_concurrency(500, *tasks)

    bad_requests = 0
    for response in results:
        if not len(response[1]):
            bad_requests += 1

    print(
        f"Total of {len(results)} Quotes, and {bad_requests} empty responses.")


async def main(symbols):
    start = pd.Timestamp('2021-05-01', tz=NY).date().isoformat()
    end = pd.Timestamp('2021-08-30', tz=NY).date().isoformat()
    timeframe: TimeFrame = TimeFrame.Day
    await get_historic_bars(symbols, start, end, timeframe)
    await get_historic_trades(symbols, start, end, timeframe)
    await get_historic_quotes(symbols, start, end, timeframe)


if __name__ == '__main__':
    """
    Credentials for this example is kept in a yaml config file.
    an example to such a file:
    
    key_id: "<YOUR-API-KEY>"
    secret: "<YOUR-API-SECRET>"
    feed: iex
    base_url: https://paper-api.alpaca.markets

    """
    import time
    import yaml

    with open("./config.yaml", mode='r') as f:
        o = yaml.safe_load(f)
        api_key_id = o.get("key_id")
        api_secret = o.get("secret")
        base_url = o.get("base_url")
        feed = o.get("feed")

    rest = AsyncRest(key_id=api_key_id,
                     secret_key=api_secret)

    api = tradeapi.REST(key_id=api_key_id,
                        secret_key=api_secret,
                        base_url=URL(base_url))

    start_time = time.time()
    loop = asyncio.get_event_loop()
    symbols = [el.symbol for el in api.list_assets()]
    symbols = symbols[:200]
    loop.run_until_complete(main(symbols))
    print(f"took {time.time() - start_time} sec")
