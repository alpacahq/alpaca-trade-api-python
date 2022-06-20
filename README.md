[![PyPI version](https://badge.fury.io/py/alpaca-trade-api.svg)](https://badge.fury.io/py/alpaca-trade-api)
[![CircleCI](https://circleci.com/gh/alpacahq/alpaca-trade-api-python.svg?style=shield)](https://circleci.com/gh/alpacahq/alpaca-trade-api-python)
[![Updates](https://pyup.io/repos/github/alpacahq/alpaca-trade-api-python/shield.svg)](https://pyup.io/repos/github/alpacahq/alpaca-trade-api-python/)
[![Python 3](https://pyup.io/repos/github/alpacahq/alpaca-trade-api-python/python-3-shield.svg)](https://pyup.io/repos/github/alpacahq/alpaca-trade-api-python/)

# alpaca-trade-api-python

`alpaca-trade-api-python` is a python library for the [Alpaca Commission Free Trading API](https://alpaca.markets).
It allows rapid trading algo development easily, with support for
both REST and streaming data interfaces. For details of each API behavior,
please see the online [API document](https://alpaca.markets/docs/api-documentation/api-v2/market-data/alpaca-data-api-v2/).

Note that this package supports only python version 3.7 and above.

## Install
We support python>=3.7. If you want to work with python 3.6, please note that these package dropped support for python <3.7 for the following versions:
```
pandas >= 1.2.0
numpy >= 1.20.0
scipy >= 1.6.0
```
The solution - manually install these packages before installing alpaca-trade-api. e.g:
```bash
pip install pandas==1.1.5 numpy==1.19.4 scipy==1.5.4
```
Also note that we do not limit the version of the websockets library, but we advise using
```
websockets>=9.0
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
* [Account/Portfolio Management](https://alpaca.markets/docs/api-documentation/api-v2)

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

You now have 2 pythonic ways to retrieve historical data.<br>
One using the traditional rest module and the other is to use the experimental asyncio module added lately.<br>
Let's have a look at both:<br>

The first thing to understand is the new data polling mechanism. You could query up to 10000 items, and the API is using a pagination mechanism to provide you with the data.<br>
You now have 2 options:
* Working with data as it is received with a generator. (meaning it's faster but you need to process each item alone)
* Wait for the entire data to be received, and then work with it as a list or dataframe.
We provide you with both options to choose from.

#### Bars
option 1: wait for the data
```py
from alpaca_trade_api.rest import REST, TimeFrame
api = REST()

api.get_bars("AAPL", TimeFrame.Hour, "2021-06-08", "2021-06-08", adjustment='raw').df

                              open      high       low     close    volume
timestamp
2021-06-08 08:00:00+00:00  126.100  126.3000  125.9600  126.3000     42107
2021-06-08 09:00:00+00:00  126.270  126.4000  126.2200  126.3800     21095
2021-06-08 10:00:00+00:00  126.380  126.6000  125.8400  126.4900     54743
2021-06-08 11:00:00+00:00  126.440  126.8700  126.4000  126.8500    206460
2021-06-08 12:00:00+00:00  126.821  126.9500  126.7000  126.9300    385164
2021-06-08 13:00:00+00:00  126.920  128.4600  126.4485  127.0250  18407398
2021-06-08 14:00:00+00:00  127.020  127.6400  126.7800  127.1350  13446961
2021-06-08 15:00:00+00:00  127.140  127.4700  126.2101  126.6100  10444099
2021-06-08 16:00:00+00:00  126.610  126.8400  126.5300  126.8250   5289556
2021-06-08 17:00:00+00:00  126.820  126.9300  126.4300  126.7072   4813459
2021-06-08 18:00:00+00:00  126.709  127.3183  126.6700  127.2850   5338455
2021-06-08 19:00:00+00:00  127.290  127.4200  126.6800  126.7400   9817083
2021-06-08 20:00:00+00:00  126.740  126.8500  126.5400  126.6600   5525520
2021-06-08 21:00:00+00:00  126.690  126.8500  126.6500  126.6600    156333
2021-06-08 22:00:00+00:00  126.690  126.7400  126.6600  126.7300     49252
2021-06-08 23:00:00+00:00  126.725  126.7600  126.6400  126.6400     41430
```
option 2: iterate over bars
```py
def process_bar(bar):
    # process bar
    print(bar)

bar_iter = api.get_bars_iter("AAPL", TimeFrame.Hour, "2021-06-08", "2021-06-08", adjustment='raw')
for bar in bar_iter:
    process_bar(bar)
```

Alternatively, you can decide on your custom timeframes by using the TimeFrame constructor:

```py
from alpaca_trade_api.rest import REST, TimeFrame, TimeFrameUnit

api = REST()
api.get_bars("AAPL", TimeFrame(45, TimeFrameUnit.Minute), "2021-06-08", "2021-06-08", adjustment='raw').df

                               open      high       low     close    volume  trade_count        vwap
timestamp
2021-06-08 07:30:00+00:00  126.1000  126.1600  125.9600  126.0600     20951          304  126.049447
2021-06-08 08:15:00+00:00  126.0500  126.3000  126.0500  126.3000     21181          349  126.231904
2021-06-08 09:00:00+00:00  126.2700  126.3200  126.2200  126.2800     15955          308  126.284120
2021-06-08 09:45:00+00:00  126.2900  126.4000  125.9000  125.9000     30179          582  126.196877
2021-06-08 10:30:00+00:00  125.9000  126.7500  125.8400  126.7500    105380         1376  126.530863
2021-06-08 11:15:00+00:00  126.7300  126.8500  126.5600  126.8300    129721         1760  126.738041
2021-06-08 12:00:00+00:00  126.4101  126.9500  126.3999  126.8300    418107         3615  126.771889
2021-06-08 12:45:00+00:00  126.8500  126.9400  126.6000  126.6200    428614         5526  126.802825
2021-06-08 13:30:00+00:00  126.6200  128.4600  126.4485  127.4150  23065023       171263  127.425797
2021-06-08 14:15:00+00:00  127.4177  127.6400  126.9300  127.1350   8535068        65753  127.342337
2021-06-08 15:00:00+00:00  127.1400  127.4700  126.2101  126.7101   8447696        64616  126.789316
2021-06-08 15:45:00+00:00  126.7200  126.8200  126.5300  126.6788   5084147        38366  126.712110
2021-06-08 16:30:00+00:00  126.6799  126.8400  126.5950  126.5950   3205870        26614  126.718837
2021-06-08 17:15:00+00:00  126.5950  126.9300  126.4300  126.7010   3908283        31922  126.665727
2021-06-08 18:00:00+00:00  126.7072  127.0900  126.6700  127.0600   3923056        29114  126.939887
2021-06-08 18:45:00+00:00  127.0500  127.4200  127.0000  127.0050   5051682        38235  127.214157
2021-06-08 19:30:00+00:00  127.0150  127.0782  126.6800  126.7800  11665598        47146  126.813182
2021-06-08 20:15:00+00:00  126.7700  126.7900  126.5400  126.6600     83725         1973  126.679259
2021-06-08 21:00:00+00:00  126.6900  126.8500  126.6700  126.7200    145153          769  126.746457
2021-06-08 21:45:00+00:00  126.7000  126.7400  126.6500  126.7100     38455          406  126.699544
2021-06-08 22:30:00+00:00  126.7100  126.7600  126.6700  126.7100     30822          222  126.713892
2021-06-08 23:15:00+00:00  126.7200  126.7600  126.6400  126.6400     32585          340  126.704131
```

#### Quotes
option 1: wait for the data
```py
from alpaca_trade_api.rest import REST
api = REST()

api.get_quotes("AAPL", "2021-06-08", "2021-06-08", limit=10).df

                                    ask_exchange  ask_price  ask_size bid_exchange  bid_price  bid_size conditions
timestamp
2021-06-08 08:00:00.070928640+00:00            P     143.00         1                    0.00         0        [Y]
2021-06-08 08:00:00.070929408+00:00            P     143.00         1            P     102.51         1        [R]
2021-06-08 08:00:00.070976768+00:00            P     143.00         1            P     116.50         1        [R]
2021-06-08 08:00:00.070978816+00:00            P     143.00         1            P     118.18         1        [R]
2021-06-08 08:00:00.071020288+00:00            P     143.00         1            P     120.00         1        [R]
2021-06-08 08:00:00.071020544+00:00            P     134.18         1            P     120.00         1        [R]
2021-06-08 08:00:00.071021312+00:00            P     134.18         1            P     123.36         1        [R]
2021-06-08 08:00:00.071209984+00:00            P     131.11         1            P     123.36         1        [R]
2021-06-08 08:00:00.071248640+00:00            P     130.13         1            P     123.36         1        [R]
2021-06-08 08:00:00.071286016+00:00            P     129.80         1            P     123.36         1        [R]
```
option 2: iterate over quotes
```py
def process_quote(quote):
    # process quote
    print(quote)

quote_iter = api.get_quotes_iter("AAPL", "2021-06-08", "2021-06-08", limit=10)
for quote in quote_iter:
    process_quote(quote)
```

#### Trades
option 1: wait for the data
```py
from alpaca_trade_api.rest import REST
api = REST()

api.get_trades("AAPL", "2021-06-08", "2021-06-08", limit=10).df

                                    exchange   price  size conditions  id tape
timestamp
2021-06-08 08:00:00.069956608+00:00        P  126.10   179     [@, T]   1    C
2021-06-08 08:00:00.207859+00:00           K  125.97     1  [@, T, I]   1    C
2021-06-08 08:00:00.207859+00:00           K  125.97    12  [@, T, I]   2    C
2021-06-08 08:00:00.207859+00:00           K  125.97     4  [@, T, I]   3    C
2021-06-08 08:00:00.207859+00:00           K  125.97     4  [@, T, I]   4    C
2021-06-08 08:00:00.207859+00:00           K  125.97     8  [@, T, I]   5    C
2021-06-08 08:00:00.207859+00:00           K  125.97     1  [@, T, I]   6    C
2021-06-08 08:00:00.207859+00:00           K  126.00    30  [@, T, I]   7    C
2021-06-08 08:00:00.207859+00:00           K  126.00    10  [@, T, I]   8    C
2021-06-08 08:00:00.207859+00:00           K  125.97    70  [@, T, I]   9    C

```
option 2: iterate over trades
```py
def process_trade(trade):
    # process trade
    print(trade)

trades_iter = api.get_trades_iter("AAPL", "2021-06-08", "2021-06-08", limit=10)
for trade in trades_iter:
    process_trade(trade)
```

### Asyncio Rest module
The `rest_async.py` module now provides an asyncion approach to retrieving the historic data.<br>
This module is, and thus may have expansions in the near future to support more endpoints.<br>
It provides a much faster way to retrieve the historic data for multiple symbols.<br>
Under the hood we use the [aiohttp](https://docs.aiohttp.org/en/stable/) library.<br>
We provide a code sample to get you started with this new approach and it is located [here](examples/historic_async.py).<br>
Follow along with the example code to learn more, and utilize it for your own needs.<br>

### Live Stream Market Data
There are 2 streams available as described [here](https://alpaca.markets/docs/market-data/#subscription-plans).

The free plan is using the `iex` stream, while the paid subscription is using the `sip` stream.

You can subscribe to bars, trades, quotes, and trade updates for your account as well.
Under the example folder you can find different [code samples](https://github.com/alpacahq/alpaca-trade-api-python/tree/master/examples/websockets)
to achieve different goals.

Here in this basic example, We use the Stream class under `alpaca_trade_api.stream` for API V2 to subscribe to trade
updates for AAPL and quote updates for IBM.
```py
from alpaca_trade_api.common import URL
from alpaca_trade_api.stream import Stream

async def trade_callback(t):
    print('trade', t)


async def quote_callback(q):
    print('quote', q)


# Initiate Class Instance
stream = Stream(<ALPACA_API_KEY>,
                <ALPACA_SECRET_KEY>,
                base_url=URL('https://paper-api.alpaca.markets'),
                data_feed='iex')  # <- replace to 'sip' if you have PRO subscription

# subscribing to event
stream.subscribe_trades(trade_callback, 'AAPL')
stream.subscribe_quotes(quote_callback, 'IBM')

stream.run()
```

#### Websockets Config For Live Data
Under the hood our SDK uses the [Websockets library](https://websockets.readthedocs.io/en/stable/index.html) to handle
our websocket connections. Since different environments can have wildly differing requirements for resources we allow you
to pass your own config options to the websockets lib via the `websocket_params` kwarg found on the Stream class.

ie:
```python
# Initiate Class Instance
stream = Stream(<ALPACA_API_KEY>,
                <ALPACA_SECRET_KEY>,
                base_url=URL('https://paper-api.alpaca.markets'),
                data_feed='iex', # <- replace to 'sip' if you have PRO subscription
                websocket_params =  {'ping_interval': 5}, #here we set ping_interval to 5 seconds 
                )
```

If you're curious [this link to their docs](https://websockets.readthedocs.io/en/stable/reference/client.html#opening-a-connection)
shows the values that websockets uses by default as well as any parameters they allow changing. Additionally, if you
don't specify any we set the following defaults on top of the ones the websockets library uses:
```python
{
    "ping_interval": 10,
    "ping_timeout": 180,
    "max_queue": 1024,
}
```


## Account & Portfolio Management

The HTTP API document is located at https://docs.alpaca.markets/

### API Version

API Version now defaults to 'v2', however, if you still have a 'v1' account, you may need to specify api_version='v1' to properly use the API until you migrate.

### Authentication

The Alpaca API requires API key ID and secret key, which you can obtain from the
web console after you sign in.  You can pass `key_id` and `secret_key` to the initializers of
`REST` or `Stream` as arguments, or set up environment variables as
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
- the original response object: `.response` property
- the HTTP status code: `.status_code` property

#### API REST Methods

| Rest Method                                                                                                                                                                                                                                      | End Point                          | Result                                                                                                                       |
|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|------------------------------------|------------------------------------------------------------------------------------------------------------------------------|
| get_account()                                                                                                                                                                                                                                    | `GET /account` and                 | `Account` entity.                                                                                                            |
| get_order_by_client_order_id(client_order_id)                                                                                                                                                                                                    | `GET /orders` with client_order_id | `Order` entity.                                                                                                              |
| list_orders(status=None, limit=None, after=None, until=None, direction=None, params=None,nested=None, symbols=None, side=None)                                                                                                                   | `GET /orders`                      | list of `Order` entities. `after` and `until` need to be string format, which you can obtain by `pd.Timestamp().isoformat()` |
| submit_order(symbol, qty=None, side="buy", type="market", time_in_force="day", limit_price=None, stop_price=None, client_order_id=None, order_class=None, take_profit=None, stop_loss=None, trail_price=None, trail_percent=None, notional=None) | `POST /orders`                     | `Order` entity.                                                                                                              |
| get_order(order_id)                                                                                                                                                                                                                              | `GET /orders/{order_id}`           | `Order` entity.                                                                                                              |
| cancel_order(order_id)                                                                                                                                                                                                                           | `DELETE /orders/{order_id}`        |                                                                                                                              |
| cancel_all_orders()                                                                                                                                                                                                                              | `DELETE /orders`                   |                                                                                                                              |
| list_positions()                                                                                                                                                                                                                                 | `GET /positions`                   | list of `Position` entities                                                                                                  |
| get_position(symbol)                                                                                                                                                                                                                             | `GET /positions/{symbol}`          | `Position` entity.                                                                                                           |
| list_assets(status=None, asset_class=None)                                                                                                                                                                                                       | `GET /assets`                      | list of `Asset` entities                                                                                                     |
| get_asset(symbol)                                                                                                                                                                                                                                | `GET /assets/{symbol}`             | `Asset` entity                                                                                                               |
| get_clock()                                                                                                                                                                                                                                      | `GET /clock`                       | `Clock` entity                                                                                                               |
| get_calendar(start=None, end=None)                                                                                                                                                                                                               | `GET /calendar`                    | `Calendar` entity                                                                                                            |
| get_portfolio_history(date_start=None, date_end=None, period=None, timeframe=None, extended_hours=None)                                                                                                                                          | `GET /account/portfolio/history`   | PortfolioHistory entity. PortfolioHistory.df can be used to get the results as a dataframe                                   |

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

For simple orders with `type='market'` and `time_in_force='day'`, you can pass a fractional amount (`qty`) or a `notional` amount (but not both). For instance, if the current market price for SPY is $300, the following calls are equivalent:

```py
api.submit_order(
    symbol='SPY',
    qty=1.5,  # fractional shares
    side='buy',
    type='market',
    time_in_force='day',
)
```

```py
api.submit_order(
    symbol='SPY',
    notional=450,  # notional value of 1.5 shares of SPY at $300
    side='buy',
    type='market',
    time_in_force='day',
)
```

---

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
The base version of this library only allows running a single algorithm due to Alpaca's limit of one websocket connection per account. For those looking to run multiple strategies, there is [alpaca-proxy-agent project.](https://github.com/shlomikushchi/alpaca-proxy-agent)

The steps to execute this are:

* Run the Alpaca Proxy Agent as described in the project's README
* Define a new environment variable: `DATA_PROXY_WS` set to the address of the proxy agent. (e.g: `DATA_PROXY_WS=ws://127.0.0.1:8765`)
* If you are using the Alpaca data stream, make sure to initiate the Stream object with the container's url: `data_url='http://127.0.0.1:8765'`
* Execute your algorithm. It will connect to the Alpaca servers through the proxy agent, allowing you to execute multiple strategies


## Raw Data vs Entity Data
By default the data returned from the api or streamed via Stream is wrapped with an Entity object for ease of use. Some users may prefer working with vanilla python objects (lists, dicts, ...). You have 2 options to get the raw data:

* Each Entity object as a `_raw` property that extract the raw data from the object.
* If you only want to work with raw data, and avoid casting to Entity (which may take more time, casting back and forth) you could pass `raw_data` argument to `Rest()` object or the `Stream()` object.

## Support and Contribution

For technical issues particular to this module, please report the
issue on this GitHub repository. Any API issues can be reported through
Alpaca's customer support.

New features, as well as bug fixes, by sending a pull request is always
welcomed.
