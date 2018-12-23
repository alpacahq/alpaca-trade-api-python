[![PyPI version](https://badge.fury.io/py/alpaca-trade-api.svg)](https://badge.fury.io/py/alpaca-trade-api)
[![CircleCI](https://circleci.com/gh/alpacahq/alpaca-trade-api-python.svg?style=shield)](https://circleci.com/gh/alpacahq/alpaca-trade-api-python)

# alpaca-trade-api-python

`alpaca-trade-api-python` is a python library for the Alpaca trade API.
It allows rapid trading algo development easily, with support for the
both REST and streaming interfaces. For details of each API behavior,
please see the online API document.

Note this module supports only python version 3.5 and above, due to
the async/await keyword use.

## Install

```bash
$ pip3 install alpaca-trade-api
```

## Example

In order to call Alpaca's trade API, you need to obtain API key pairs.
Replace <key_id> and <secret_key> with what you get from the web console.

### REST example
```python
import alpaca_trade_api as tradeapi

api = tradeapi.REST('<key_id>', '<secret_key>')
account = api.get_account()
api.list_positions()
```

## API Document

The HTTP API document is located in https://docs.alpaca.markets/

## Authentication

The Alpaca API requires API key ID and secret key, which you can obtain from the
web console after you sign in.  You can pass `key_id` and `secret_key` to the initializers of
`REST` or `StreamConn` as arguments, or set up environment variables as
follows.

- APCA_API_KEY_ID: key ID
- APCA_API_SECRET_KEY: secret key

## Base URL

The base URL for API calls defaults to `https://api.alpaca.markets/`. This endpoint
is for live trading, and for paper trading and other purposes, you can to change
the base URL. You can pass `base_url` kwarg to `REST()`, or using the environment
variable, `APCA_API_BASE_URL`.

The environment variable `APCA_API_DATA_URL` can also be changed to configure the
endpoint for returning data from the `/bars` endpoint. By default, it will use
`https://data.alpaca.markets`.

## REST

The `REST` class is the entry point for the API request.  The instance of this
class provides all REST API calls such as account, orders, positions,
and bars.

Each returned object is wrapped by a subclass of `Entity` class (or a list of it).
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

The `Entity` class also converts timestamp string field to a pandas.Timestamp
object.  Its `_raw` property returns the original raw primitive data unmarshaled
from the response JSON text.

When a REST API call sees the 429 or 504 status code, this library retries 3 times
by default, with 3 seconds apart between each call. These are configurable with
the following environment variables.

- APCA_RETRY_MAX: the number of subsequent API calls to retry, defaults to 3
- APCA_RETRY_WAIT: seconds to wait between each call, defaults to 3
- APCA_RETRY_CODES: comma-separated HTTP status code for which retry is attempted

If the retry exceeds, or other API error is returned, `alpaca_trade_api.rest.APIError` is raised.
You can access the following information through this object.

- the API error code: `.code` property
- the API error message: `str(error)`
- the original request object: `.request` property
- the original response objecgt: `.response` property
- the HTTP status code: `.status_code` property

### REST.get_account()
Calls `GET /account` and returns an `Account` entity.

### REST.list_orders(status=None, limit=None, after=None, until=None, direction=None)
Calls `GET /orders` and returns a list of `Order` entities.
`after` and `until` need to be string format, which you can obtain by `pd.Timestamp().isoformat()`

### REST.submit_order(symbol, qty, side, type, time_in_force, limit_price=None, stop_price=None, client_order_id=None)
Calls `POST /orders` and returns an `Order` entity.

### REST.get_order_by_client_order_id(client_order_id)
Calls `GET /orders` with client_order_id and returns an `Order` entity.

### REST.get_order(order_id)
Calls `GET /orders/{order_id}` and returns an `Order` entity.

### REST.cancel_order(order_id)
Calls `DELETE /orders/{order_id}`.

### REST.list_positions()
Calls `GET /positions` and returns a list of `Position` entities.

### REST.get_position(symbol)
Calls `GET /positions/{symbol}` and returns a `Position` entity.

### REST.list_assets(status=None, asset_class=None)
Calls `GET /assets` and returns a list of `Asset` entities.

### REST.get_asset(symbol)
Calls `GET /assets/{symbol}` and returns an `Asset` entity.

### REST.get_barset(symbols, timeframe, limit, start=None, end=None, after=None, until=None)
Calls `GET /bars/{timeframe}` for the given symbols, and returns a Barset with `limit` Bar objects
for each of the the requested symbols.
`timeframe` can be one of `minute`, `1Min`, `5Min`, `15Min`, `day` or `1D`. `minute` is an alias
of `1Min`. Similarly, `day` is an alias of `1D`.
`start`, `end`, `after`, and `until` need to be string format, which you can obtain with
`pd.Timestamp().isoformat()`
`after` cannot be used with `start` and `until` cannot be used with `end`.

### REST.get_clock()
Calls `GET /clock` and returns a `Clock` entity.

### REST.get_calendar(start=None, end=None)
Calls `GET /calendar` and returns a `Calendar` entity.

---

## StreamConn

The `StreamConn` class provides WebSocket/NATS-based event-driven
interfaces.  Using the `on` decorator of the instance, you can
define custom event handlers that are called when the pattern
is matched on the channel name.  Once event handlers are set up,
call the `run` method which runs forever until a critical exception
is raised. This module itself does not provide any threading
capability, so if you need to consume the messages pushed from the
server, you need to run it in a background thread.

This class provides a unique interface to the two interfaces, both
Alpaca's account/trade updates events and Polygon's price updates.
One connection is established when the `subscribe()` is called with
the corresponding channel names.  For example, if you subscribe to
`account_updates`, a WebSocket connects to Alpaca stream API, and
if `AM.*` given to the `subscribe()` method, a NATS connection is
established to Polygon's interface.

The `run` method is a short-cut to start subscribing to channels and
runnnig forever.  The call will be blocked forever until a critical
exception is raised, and each event handler is called asynchronously
upon the message arrivals.

The `run` method tries to reconnect to the server in the event of
connection failure.  In this case you may want to reset your state
which is best in the `connect` event.  The method still raises
exception in the case any other unknown error happens inside the
event loop.

The `msg` object passed to each handler is wrapped by the entity
helper class if the message is from the server.

Each event handler has to be a marked as `async`.  Otherwise,
a `ValueError` is raised when registering it as an event handler.

```python
conn = StreamConn()

@conn.on(r'account_updates')
async def on_account_updates(conn, channel, account):
    print('account', account)


@conn.on(r'^AM.')
def on_bars(conn, channel, bar):
    print('bars', bar)


# blocks forever
conn.run(['account_updates', 'AM.*'])

```

You will likely call the `run` method in a thread since it will keep running
unless an exception is raised.

### StreamConn.subscribe(channels)
Request "listen" to the server.  `channels` must be a list of string channel names.

### StreamConn.run(channels)
Goes into an infinite loop and awaits for messages from the server.  You should
set up event listeners using the `on` or `register` method before calling `run`.

### StreamConn.on(channel_pat)
As in the above example, this is a decorator method to add an event handler function.
`channel_pat` is used as a regular expression pattern to filter stream names.

### StreamConn.register(channel_pat, func)
Registers a function as an event handler that is triggered by the stream events
that match with `channel_path` regular expression. Calling this method with the
same `channel_pat` will overwrite the old handler.

### StreamConn.deregister(channel_pat)
Deregisters the event handler function that was previously registered via `on` or
`register` method.


---
# Polygon API Service

Alpaca's API key ID can be used to access Polygon API whose document is found [here](https://polygon.io/docs/).
This python SDK wraps their API service and seamlessly integrates with Alpaca API.
`alpaca_trade_api.REST.polygon` will be the `REST` object for Polygon.

The example below gives AAPL daily OHLCV data in a DataFrame format.

```py
import alpaca_trade_api as tradeapi

api = tradeapi.REST()
aapl = api.polygon.historic_agg('day', 'AAPL', limit=1000).df
```

## polygon/REST
It is initialized through alpaca `REST` object.

### polygon/REST.exchanges()
Returns a list of `Exchange` entity.

### polygon/REST.symbol_type_map()
Returns a `SymbolTypeMap` object.

### polygon/REST.historic_trades(symbol, date, offset=None, limit=None)
Returns a `Trades` which is a list of `Trade` entities.

- `date` is a date string such as '2018-2-2'.  The returned quotes are from this day onyl.
- `offset` is an integer in Unix Epoch millisecond as the lower bound filter, inclusive.
- `limit` is an integer for the number of ticks to return.  Default and max is 30000.

### polygon/Trades.df
Returns a pandas DataFrame object with the ticks returned by the `historic_trades`.

### polygon/REST.historic_quotes(symbol, date, offset=None, limit=None)
Returns a `Quotes` which is a list of `Quote` entities.

- `date` is a date string such as '2018-2-2'. The returned quotes are from this day only.
- `offset` is an integer in Unix Epoch millisecond as the lower bound filter, inclusive.
- `limit` is an integer for the number of ticks to return.  Default and max is 30000.

### polygon/Quotes.df
Returns a pandas DataFrame object with the ticks returned by the `historic_quotes`.

### polygon/REST.historic_agg(size, symbol, _from=None, to=None, limit=None)
Returns an `Aggs` which is a list of `Agg` entities. `Aggs.df` gives you the DataFrame
object.

- `_from` is an Eastern Time timestamp string that filters the result for the lower bound, inclusive.
- `to` is an Eastern Time timestamp string that filters the result for the upper bound, inclusive.
- `limit` is an integer to limit the number of results.  3000 is the default and max value.

Specify the `_from` parameter if you specify the `to` parameter since when `to` is
specified `_from` is assumed to be the beginning of history.  Otherwise, when you
use only the `limit` or no parameters, the result is returned from the latest point.

The returned entities have fields relabeled with the longer name instead of shorter ones.
For example, the `o` field is renamed to `open`.

### polygon/Aggs.df
Returns a pandas DataFrame object with the ticks returned by the `hitoric_agg`.

### poylgon/REST.last_trade(symbol)
Returns a `Trade` entity representing the last trade for the symbol.

### polygon/REST.last_quote(symbol)
Returns a `Quote` entity representing the last quote for the symbol.

### polygon/REST.condition_map(ticktype='trades')
Returns a `ConditionMap` entity.

### polygon/REST.company(symbol)
Returns a `Company` entity if `symbol` is string, or a
dict[symbol -> `Company`] if `symbol` is a list of string.

### polygon/REST.dividends(symbol)
Returns a `Dividends` entity if `symbol` is string, or a
dict[symbol -> `Dividends`] if `symbol is a list of string.

### polygon/REST.splits(symbol)
Returns a `Splits` entity for the symbol.

### polygon/REST.earnings(symbol)
Returns an `Earnings` entity if `symbol` is string, or a
dict[symbol -> `Earnings`] if `symbol` is a list of string.

### polygon/REST.financials(symbol)
Returns an `Financials` entity if `symbol` is string, or a
dict[symbol -> `Financials`] if `symbol` is a list of string.

### polygon/REST.news(symbol)
Returns a `NewsList` entity for the symbol.


## Support and Contribution

For technical issues particular to this module, please report the
issue on this GitHub repository. Any API issues can be reported through
Alpaca's customer support.

New features, as well as bug fixes, by sending pull request is always
welcomed.
