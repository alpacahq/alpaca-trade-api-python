import os
import sys
import asyncio
import alpaca_trade_api as tradeapi
from alpaca_trade_api.rest import TimeFrame, URL
from alpaca_trade_api.rest_async import gather_with_concurrency, AsyncRest
import pandas as pd
from enum import Enum

NY = 'America/New_York'


class DataType(str, Enum):
    Bars = "Bars"
    Trades = "Trades"
    Quotes = "Quotes"


def get_data_method(data_type: DataType):
    if data_type == DataType.Bars:
        return rest.get_bars_async
    elif data_type == DataType.Trades:
        return rest.get_trades_async
    elif data_type == DataType.Quotes:
        return rest.get_quotes_async
    else:
        raise Exception(f"Unsupoported data type: {data_type}")


async def get_historic_data_base(symbols, data_type: DataType, start, end,
                                 timeframe: TimeFrame):
    """
    base function to use with all
    :param symbols:
    :param start:
    :param end:
    :param timeframe:
    :return:
    """
    major = sys.version_info.major
    minor = sys.version_info.minor
    if major < 3 or minor < 6:
        raise Exception('asyncio is not support in your python version')
    print(
        f"Getting {data_type} data for {len(symbols)} symbols, timeframe: "
        f"{timeframe} between dates: start={start}, end={end}")

    tasks = []

    for symbol in symbols:
        tasks.append(
            get_data_method(data_type)(symbol, start, end, timeframe,
                                       limit=500))
    if minor >= 8:
        results = await asyncio.gather(*tasks, return_exceptions=True)
    else:
        results = await gather_with_concurrency(500, *tasks)

    bad_requests = 0
    for response in results:
        if isinstance(response, Exception):
            print(f"Got an error: {response}")
        elif not len(response[1]):
            bad_requests += 1

    print(f"Total of {len(results)} {data_type}, and {bad_requests} "
          f"empty responses.")


async def get_historic_bars(symbols, start, end, timeframe: TimeFrame):
    await get_historic_data_base(symbols, DataType.Bars, start, end, timeframe)


async def get_historic_trades(symbols, start, end, timeframe: TimeFrame):
    await get_historic_data_base(symbols, DataType.Trades, start, end,
                                 timeframe)


async def get_historic_quotes(symbols, start, end, timeframe: TimeFrame):
    await get_historic_data_base(symbols, DataType.Quotes, start, end,
                                 timeframe)


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
        api_key_id = o.get("key_id") or os.environ.get('APCA_API_KEY_ID')
        api_secret = o.get("secret") or os.environ.get('APCA_API_SECRET_KEY')
        base_url = o.get("base_url") or "https://paper-api.alpaca.markets"
        feed = o.get("feed") or "iex"

    rest = AsyncRest(key_id=api_key_id,
                     secret_key=api_secret)

    api = tradeapi.REST(key_id=api_key_id,
                        secret_key=api_secret,
                        base_url=URL(base_url))

    start_time = time.time()
    loop = asyncio.get_event_loop()
    symbols = [el.symbol for el in api.list_assets(status='active')]
    symbols = symbols[:200]
    loop.run_until_complete(main(symbols))
    print(f"took {time.time() - start_time} sec")
