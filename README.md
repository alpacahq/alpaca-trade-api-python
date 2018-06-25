# alpaca-trade-api-python

`alpaca-trade-api-python` is a python library for the Alpaca trade API.
It allows rapid trading algo development easily, with support for the
both REST and streaming interfaces. For details of each API behavior,
please see the online API document.

## Install

```bash
$ pip install alpaca-trade-api
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

### Streaming example
```python
import alpaca_trade_api as tradeapi

conn = tradeapi.StreamConn('<key_id>', '<secret_key>')

# Setup event handlers
@conn.on('authenticated')
def on_auth(conn, stream, msg):
    conn.subscribe([
        'account_updates',
        'trade_updates',
        'quotes/AAPL',
        ])

@conn.on(r'quotes/')
def on_quotes(conn, stream, msg):
    print('quotes', msg)

@conn.on(r'account_updates')
def on_account(conn, stream, msg):
    print('account', msg)

# blocks forever
conn.run()
```

## API Document

The HTTP API document is located in https://docs.alpaca.markets/

## Authentication

The Alpaca API requires API key ID and secret key, which you can obtain from the
web console after you sign in.  You can give them to the initializers of
`REST` or `StreamConn` as arguments, or set up environment variables as
follows.

- APCA_API_KEY_ID: key ID
- APCA_API_SECRET_KEY: secret key

## REST

The `REST` class is the entry point for the API request.  The instance of this
class provides all REST API calls such as account, orders, positions,
bars, quotes and fundamentals.

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

When a REST API call sees the 429 status code, this library retries 3 times
by default, with 3 seconds apart between each call. These are configurable with
the following environment variables.

- APCA_MAX_RETRY: the number of subsequent API calls to retry, defaults to 3
- APCA_RETRY_WAIT: seconds to wait between each call, defaults to 3

### REST.get_account()
Calls `GET /account` and returns an `Account` entity.

### REST.list_orders(status=None)
Calls `GET /orders` and returns a list of `Order` entities.

### REST.submit_order(symbol, qty, side, type, time_in_force, limit_price=None, stop_price=None, client_order_id=None)
Calls `POST /orders` and returns an `Order` entity.

### REST.get_order_by_client_order_id(client_order_id)
Calls `GET /orders` with client_order_id and returns an `Order` entity.

### REST.get_order(order_id)
Calls `GET /orders/{order_id}` and returns an `Order` entity.

### REST.cancel_order(order_id)
Calls `DELETE /orders/{order_id}`.

### REST.list_position()
Calls `GET /positions` and returns a list of `Position` entities.

### REST.get_position(symbol)
Calls `GET /positions/{symbol}` and returns a `Position` entity.

### REST.list_assets(status=None, asset_class=None)
Calls `GET /assets` and returns a list of `Asset` entities.

### REST.get_asset(symbol)
Calls `GET /assets/{symbol}` and returns an `Asset` entity.

### REST.get_clock()
Calls `GET /clock` and returns a `Clock` entity.

### REST.get_calendar(start=None, end=None)
Calls `GET /calendar` and returns a `Calendar` entity.

### REST.list_quotes(symbols)
\*** The method is being deprecated. Use Polygon API

Calls `GET /quotes` with symbols and returns a list of `Quote` entities.  If `symbols` is not a string, it is concatenated with commas.

### REST.get_quote(symbol)
\*** The method is being deprecated. Use Polygon API

Calls `GET /assets/{symbol}/quote` and returns a `Quote` entity.

### REST.list_fundamentals(symbols)
\*** The method is being deprecated. Use Polygon API

Calls `GET /fundamentals` with symbols and returns a list of `Fundamental` entities.
If `symbols` is not a string, it is concatenated with commas.

### REST.get_fundamental(symbol)
\*** The method is being deprecated. Use Polygon API

Calls `GET /assets/{symbol}/fundamental` and returns a `Fundamental` entity.

### REST.list_bars(symbols, timeframe, start_dt=None, end_dt=None, limit=None)
\*** The method is being deprecated. Use Polygon API

Calls `GET /bars` and returns a list of `AssetBars` entities. If `symbols` is
not a string, it is concatenated with commas. `start_dt` and `end_dt` should be
in the ISO8601 string format.

### REST.get_bars(symbol, timeframe, start_dt=None, end_dt=None, limit=None)
\*** The method is being deprecated. Use Polygon API

Calls `GET /assets/{symbol}/bars` with parameters and returns an `AssetBars`
entity.  `start_dt` and `end_dt` should be in the ISO8601 string format.

### AssetBars.df
Returns a DataFrame constructed from the Bars response.  The property is cached.

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

You will likely call the `run` method in a thread since it will keep runnig
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


## Support and Contribution

For technical issues particular to this module, please report the
issue on this GitHub repository. Any API issues can be reported through
Alpaca's customer support.

New features, as well as bug fixes, by sending pull request is always
welcomed.


---
# Polygon API Service

Alpaca's API key ID can be used to access Polygon API whose document is found [here](https://polygon.io/docs).
This python SDK wraps their API service and seamlessly integrates with Alpaca API.
`alpaca_trade_api.REST.polygon` will be the `REST` object for Polygon.

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
