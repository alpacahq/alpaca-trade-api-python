[![PyPI version](https://badge.fury.io/py/alpaca-trade-api.svg)](https://badge.fury.io/py/alpaca-trade-api)
[![CircleCI](https://circleci.com/gh/alpacahq/alpaca-trade-api-python.svg?style=shield)](https://circleci.com/gh/alpacahq/alpaca-trade-api-python)
[![Updates](https://pyup.io/repos/github/alpacahq/alpaca-trade-api-python/shield.svg)](https://pyup.io/repos/github/alpacahq/alpaca-trade-api-python/)
[![Python 3](https://pyup.io/repos/github/alpacahq/alpaca-trade-api-python/python-3-shield.svg)](https://pyup.io/repos/github/alpacahq/alpaca-trade-api-python/)

# alpaca-trade-api-python

`alpaca-trade-api-python` is a python library for the [Alpaca Commission Free Trading API](https://alpaca.markets).
It allows rapid trading algo development easily, with support for
both REST and streaming data interfaces. For details of each API behavior,
please see the online [API document](https://alpaca.markets/docs/api-documentation/api-v2/market-data/alpaca-data-api-v2/).

Note that this package supports only python version 3.6 and above, due to
the async/await and websockets module dependency.

## Install
We support python>=3.6. If you want to work with python 3.6, please note that these package dropped support for python <3.7 for the following versions:
```
pandas >= 1.2.0
numpy >= 1.20.0
scipy >= 1.6.0
```
The solution - manually install these package before installing alpaca-trade-api. e.g:
```bash
pip install pandas==1.1.5 numpy==1.19.4 scipy==1.5.4
```

Installing using pip
```bash
$ pip3 install alpaca-trade-api
```

## API Keys
To use this package you first need to obtain an API key. Go here to [signup](https://app.alpaca.markets/signup)

# Services
These services are provided by Alpaca:
* Data:
  * [Historical](https://alpaca.markets/docs/api-documentation/api-v2/market-data/alpaca-data-api-v2/historical/)
  * [Live Data Stream](https://alpaca.markets/docs/api-documentation/api-v2/market-data/alpaca-data-api-v2/real-time/)
* [Account/Porfolio Management](https://alpaca.markets/docs/api-documentation/api-v2)

The free services are limited, please check the docs to see the differences between paid/free services.

## Alpaca Environment Variables

The Alpaca SDK will check the environment for a number of variables that can be used rather than hard-coding these into your scripts.<br>
Alternatively you could pass the credentials directly to the SDK instances.


| Environment                      | default                                                                                | Description                                                                                                            |
| -------------------------------- | -------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------- |
| APCA_API_KEY_ID=<key_id>         |                                                                                        | Your API Key                                                                                                           |
| APCA_API_SECRET_KEY=<secret_key> |                                                                                        | Your API Secret Key                                                                                                    |
| APCA_API_BASE_URL=url            | https://api.alpaca.markets (for live) | Specify the URL for API calls, *Default is live, you must specify <br/>https://paper-api.alpaca.markets to switch to paper endpoint!*                   |
| APCA_API_DATA_URL=url            | https://data.alpaca.markets                                                            | Endpoint for data API                                                                                                  |
| APCA_RETRY_MAX=3                 | 3                                                                                      | The number of subsequent API calls to retry on timeouts                                                                |
| APCA_RETRY_WAIT=3                | 3                                                                                      | seconds to wait between each retry attempt                                                                             |
| APCA_RETRY_CODES=429,504         | 429,504                                                                                | comma-separated HTTP status code for which retry is attempted                                                          |
| DATA_PROXY_WS                    |                                                                                        | When using the alpaca-proxy-agent you need to set this environment variable as described ![here](https://github.com/shlomikushchi/alpaca-proxy-agent) |

## Working with Data
### Historic Data
You could get one of these historic data types:
* Bars
* Quotes
* Trades
First thing to understand is the new data polling mechanism. You could query up to 10000 items, and the API is using a pagination mechanism to provide you with the data.<br>
You now have 2 options:
* Working with data as it is received with a generator. (meaning it's faster but you need to process each item alone)
* Wait for the entire data to be received, and then work with it as a list or dataframe.
We provide you with both options to choose from.

#### Bars
option 1: wait for the data
```py
from alpaca_trade_api.rest import REST
api = REST()

api.get_bars("AAPL", TimeFrame.Hour, "2021-02-08", "2021-02-08", limit=10, adjustment='raw').df

                               open    high      low     close    volume
timestamp                                                               
2021-02-08 09:00:00+00:00  136.6800  137.15  136.450  136.9600     38707
2021-02-08 10:00:00+00:00  136.9600  137.08  136.800  136.8300     22334
2021-02-08 11:00:00+00:00  136.8300  136.97  136.710  136.9100     19546
2021-02-08 12:00:00+00:00  136.9000  136.97  136.050  136.2200    483167
2021-02-08 13:00:00+00:00  136.2200  136.25  136.010  136.1700    307755
2021-02-08 14:00:00+00:00  136.1525  136.35  134.920  135.6900  12159693
2021-02-08 15:00:00+00:00  135.6800  136.68  135.595  136.6100   8076122
2021-02-08 16:00:00+00:00  136.6800  136.91  135.040  136.2350   8484923
2021-02-08 17:00:00+00:00  136.2400  136.54  135.030  135.9745   4610247
2021-02-08 18:00:00+00:00  135.9799  136.30  135.800  135.9330   3375300
```
option 2: iterate over bars
```py
def process_bar(bar):
    # process bar
    print(bar)

bar_iter = api.get_bars_iter("AAPL", TimeFrame.Hour, "2021-02-08", "2021-02-08", limit=10, adjustment='raw')
for bar in bar_iter:
    process_bar(bar)
```

#### Quotes
option 1: wait for the data
```py
from alpaca_trade_api.rest import REST
api = REST()

api.get_quotes("AAPL", "2021-02-08", "2021-02-08", limit=10).df

                                    ask_exchange  ask_price  ask_size bid_exchange  bid_price  bid_size conditions
timestamp                                                                                                         
2021-02-08 09:02:07.697204555+00:00            Q     136.80         1            P     136.52         1        [R]
2021-02-08 09:02:07.706401536+00:00            Q     136.80         1            P     136.56         2        [R]
2021-02-08 09:02:07.837365238+00:00            P     136.81         1            P     136.56         2        [R]
2021-02-08 09:02:07.838885705+00:00            Q     136.79         1            P     136.56         2        [R]
2021-02-08 09:02:30.946732544+00:00            P     136.64         1            P     136.50         1        [R]
2021-02-08 09:02:32.558048512+00:00            P     136.64         1            P     136.37         1        [R]
2021-02-08 09:02:32.794415360+00:00            Q     136.69         1            P     136.37         1        [R]
2021-02-08 09:02:32.795173632+00:00            P     136.62         1            P     136.37         1        [R]
2021-02-08 09:02:33.969686528+00:00            Q     136.69         1            P     136.37         1        [R]
2021-02-08 09:02:34.069692672+00:00            P     136.55         1            P     136.37         1        [R]

```
option 2: iterate over quotes
```py
def process_quote(quote):
    # process quote
    print(quote)

quote_iter = api.get_quotes_iter("AAPL", "2021-02-08", "2021-02-08", limit=10)
for quote in quote_iter:
    process_quote(quote)
```

#### Trades
option 1: wait for the data
```py
from alpaca_trade_api.rest import REST
api = REST()

api.get_trades("AAPL", "2021-02-08", "2021-02-08", limit=10).df

                                    exchange   price  size conditions  id tape
timestamp                                                                     
2021-02-08 09:00:11.764828160+00:00        P  136.68     1  [@, T, I]  46    C
2021-02-08 09:00:13.885322240+00:00        P  136.75    35  [@, T, I]  49    C
2021-02-08 09:00:13.885322240+00:00        P  136.75    10  [@, T, I]  48    C
2021-02-08 09:00:13.885322240+00:00        P  136.68    28  [@, T, I]  47    C
2021-02-08 09:00:17.024569856+00:00        P  136.61    16  [@, T, I]  50    C
2021-02-08 09:00:17.810107904+00:00        P  136.66     1  [@, T, I]  51    C
2021-02-08 09:00:19.932405248+00:00        P  136.68    25  [@, T, I]  55    C
2021-02-08 09:00:19.932405248+00:00        P  136.75    18  [@, T, I]  56    C
2021-02-08 09:00:19.932405248+00:00        P  136.68    11  [@, T, I]  54    C
2021-02-08 09:00:19.932405248+00:00        P  136.67    10  [@, T, I]  53    C

```
option 2: iterate over trades
```py
def process_trade(trade):
    # process trade
    print(trade)

trades_iter = api.get_trades_iter("AAPL", "2021-02-08", "2021-02-08", limit=10)
for trade in trades_iter:
    process_trade(trade)
```

### Live Stream Data
There are 2 streams available as described [here](https://alpaca.markets/docs/api-documentation/api-v2/market-data/alpaca-data-api-v2/real-time/).<br>
The free plan is using the `iex` stream, while the paid subscription is using the `sip` stream.<br>
You could subscribe to bars, trades or quotes and accoutn updates as well.<br>
Under the example folder you could find different code [samples](https://github.com/alpacahq/alpaca-trade-api-python/tree/feature/data-v2/examples/websockets) to achieve different goals. Let's see the basic example<br>
We present a new Streamer class under `alpaca_trade_api.stream` for API V2.
```py

async def trade_callback(t):
    print('trade', t)


async def quote_callback(q):
    print('quote', q)


# Initiate Class Instance
stream = Stream(<ALPACA_API_KEY>,
                <ALPACA_SECRET_KEY>,
                base_url=URL('https://paper-api.alpaca.markets'),
                data_feed='iex')  # <- replace to SIP if you have PRO subscription

# subscribing to event
stream.subscribe_trades(trade_callback, 'AAPL')
stream.subscribe_quotes(quote_callback, 'IBM')

stream.run()

```

## Acount & Portfolio Management 

The HTTP API document is located at https://docs.alpaca.markets/

### API Version

API Version now defaults to 'v2', however, if you still have a 'v1' account, you may need to specify api_version='v1' to properly use the API until you migrate.

### Authentication

The Alpaca API requires API key ID and secret key, which you can obtain from the
web console after you sign in.  You can pass `key_id` and `secret_key` to the initializers of
`REST` or `StreamConn` as arguments, or set up environment variables as
outlined below.

### REST

The `REST` class is the entry point for the API request.  The instance of this
class provides all REST API calls such as account, orders, positions,
and bars.

Each returned object is wrapped by a subclass of the `Entity` class (or a list of it).
This helper class provides property access (the "dot notation") to the
json object, backed by the original object stored in the `_raw` field.
It also converts certain types to the appropriate python object.

```python
import alpaca_trade_api as tradeapi

api = tradeapi.REST()
account = api.get_account()
account.status
=> 'ACTIVE'
```

The `Entity` class also converts the timestamp string field to a pandas.Timestamp
object.  Its `_raw` property returns the original raw primitive data unmarshaled
from the response JSON text.

Please note that the API is throttled, currently 200 requests per minute, per account.  If your client exceeds this number, a 429 Too many requests status will be returned and this library will retry according to the retry environment variables as configured.

If the retries are exceeded, or other API error is returned, `alpaca_trade_api.rest.APIError` is raised.
You can access the following information through this object.
- the API error code: `.code` property
- the API error message: `str(error)`
- the original request object: `.request` property
- the original response objecgt: `.response` property
- the HTTP status code: `.status_code` property

#### API REST Methods

| Rest Method                                      | End Point          |   Result                                                                                | 
| --------------------------------                 | -------------------| ------------------------------------------------------------------ |
| get_account()                                    | `GET /account` and | `Account` entity.|
| get_order_by_client_order_id(client_order_id)    | `GET /orders` with client_order_id | `Order` entity.|
| list_orders(status=None, limit=None, after=None, until=None, direction=None, nested=None) | `GET /orders` | list of `Order` entities. `after` and `until` need to be string format, which you can obtain by `pd.Timestamp().isoformat()` |
| submit_order(symbol, qty, side, type, time_in_force, limit_price=None, stop_price=None, client_order_id=None, order_class=None, take_profit=None, stop_loss=None, trail_price=None, trail_percent=None)| `POST /orders` |  `Order` entity. |
| get_order(order_id)                              | `GET /orders/{order_id}` | `Order` entity.|
| cancel_order(order_id)                           | `DELETE /orders/{order_id}` | |
| cancel_all_orders()                              | `DELETE /orders`| |
| list_positions()                                 | `GET /positions` | list of `Position` entities|
| get_position(symbol)                             | `GET /positions/{symbol}` | `Position` entity.|
| list_assets(status=None, asset_class=None)       | `GET /assets` | list of `Asset` entities|
| get_asset(symbol)                                | `GET /assets/{symbol}` | `Asset` entity|
| get_barset(symbols, timeframe, limit, start=None, end=None, after=None, until=None) | `GET /bars/{timeframe}` | Barset with `limit` Bar objects for each of the the requested symbols. `timeframe` can be one of `minute`, `1Min`, `5Min`, `15Min`, `day` or `1D`. `minute` is an alias of `1Min`. Similarly, `day` is an alias of `1D`. `start`, `end`, `after`, and `until` need to be string format, which you can obtain with `pd.Timestamp().isoformat()` `after` cannot be used with `start` and `until` cannot be used with `end`.|
| get_aggs(symbol, timespan, multiplier, _from, to)| `GET /aggs/ticker/{symbol}/range/{multiplier}/{timespan}/{from}/{to}` | `Aggs` entity. `multiplier` is the size of the timespan multiplier. `timespan` is the size of the time window, can be one of `minute`, `hour`, `day`, `week`, `month`, `quarter` or `year`. `_from` and `to` must be in `YYYY-MM-DD` format, e.g. `2020-01-15`.| 
| get_last_trade(symbol)                           | `GET /last/stocks/{symbol}` | `Trade` entity|
| get_last_quote(symbol)                           | `GET /last_quote/stocks/{symbol}` | `Quote` entity|
| get_clock()                                      | `GET /clock` | `Clock` entity|
| get_calendar(start=None, end=None)               | `GET /calendar` | `Calendar` entity|
| get_portfolio_history(date_start=None, date_end=None, period=None, timeframe=None, extended_hours=None) | `GET /account/portfolio/history` | PortfolioHistory entity. PortfolioHistory.df can be used to get the results as a dataframe|

#### Rest Examples

Please see the `examples/` folder for some example scripts that make use of this API

##### Using `submit_order()`
Below is an example of submitting a bracket order.
```py
api.submit_order(
    symbol='SPY',
    side='buy',
    type='market',
    qty='100',
    time_in_force='day',
    order_class='bracket',
    take_profit=dict(
        limit_price='305.0',
    ),
    stop_loss=dict(
        stop_price='295.5',
        limit_price='295.5',
    )
)
```

##### Using `get_barset()` (Deprecated. use `get_bars()` instead)
```python 
import pandas as pd
NY = 'America/New_York'
start=pd.Timestamp('2020-08-01', tz=NY).isoformat()
end=pd.Timestamp('2020-08-30', tz=NY).isoformat()
print(api.get_barset(['AAPL', 'GOOG'], 'day', start=start, end=end).df)

# Minute data example
start=pd.Timestamp('2020-08-28 9:30', tz=NY).isoformat()
end=pd.Timestamp('2020-08-28 16:00', tz=NY).isoformat()
print(api.get_barset(['AAPL', 'GOOG'], 'minute', start=start, end=end).df)

```

please note that if you are using limit, it is calculated from the end date. and if end date is not specified, "now" is used. <br>Take that under consideration when using start date with a limit. 

---

#### Debugging
Websocket exceptions may occur during execution.
It will usually happen during the `consume()` method, which basically is the 
websocket steady-state.<br>
exceptions during the consume method may occur due to:
- server disconnections
- error while handling the response data

We handle the first issue by reconnecting the websocket every time there's a disconnection.
The second issue, is usually a user's code issue. To help you find it, we added a flag to the 
StreamConn object called `debug`. It is set to False by default, but you can turn it on to get a more
verbose logs when this exception happens.
Turn it on like so `StreamConn(debug=True)`  

## Logging
You should define a logger in your app in order to make sure you get all the messages from the different components.<br>
It will help you debug, and make sure you don't miss issues when they occur.<br>
The simplest way to define a logger, if you have no experience with the python logger - will be something like this:
```py
import logging
logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)
```

## Websocket best practices
Under the examples folder you could find several examples to do the following:
* Different subscriptions(channels) usage with the alpaca streams
* pause / resume connection
* change subscriptions/channels of existing connection
* ws disconnections handler (make sure we reconnect when the internal mechanism fails)


## Running Multiple Strategies
There's a way to execute more than one algorithm at once.<br>
The websocket connection is limited to 1 connection per account. <br>
For that exact purpose this ![project](https://github.com/shlomikushchi/alpaca-proxy-agent)  was created<br>
The steps to execute this are:
* Run the Alpaca Proxy Agent as described in the project's README
* Define this env variable: `DATA_PROXY_WS` to be the address of the proxy agent. (e.g: `DATA_PROXY_WS=ws://127.0.0.1:8765`)
* If you are using the Alpaca data stream, make sure you you initiate the StreamConn object with the container's url, like so: data_url='http://127.0.0.1:8765'
* execute your algorithm. it will connect to the servers through the proxy agent allowing you to execute multiple strategies


## Raw Data vs Entity Data
By default the data returned from the api or streamed via StreamConn is wrapped with an Entity object for ease of use.<br>
Some users may prefer working with raw python objects (lists, dicts, ...). <br>You have 2 options to get the raw data:
* Each Entity object as a `_raw` property that extract the raw data from the object.
* If you only want to work with raw data, and avoid casting to Entity (which may take more time, casting back and forth) <br>you could pass `raw_data` argument
  to `Rest()` object or the `StreamConn()` object.

## Support and Contribution

For technical issues particular to this module, please report the
issue on this GitHub repository. Any API issues can be reported through
Alpaca's customer support.

New features, as well as bug fixes, by sending a pull request is always
welcomed.
