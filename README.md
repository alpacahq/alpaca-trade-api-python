# alpaca-trade-api-python

`alpaca-trade-api-python` is a python library for the Alpaca trade API.
It allows rapid trading algo development easily, with support for the
both REST and streaming interfaces. For details of each API behavior,
please see the online API document.

## Install

```bash
$ pip install alpaca-trade-api-python
```

## Example

In order to call Alpaca's trade API, you need to obtain API key pairs.
Replace <key_id> and <secret_key> with what you get from the
web console.

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
object.

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

### REST.list_quotes(symbols)
Calls `GET /quotes` with symbols and returns a list of `Quote` entities.  If `symbols` is not a string, it is concatenated with commas.

### REST.get_quote(symbol)
Calls `GET /assets/{symbol}/quote` and returns a `Quote` entity.

### REST.list_fundamentals(symbols)
Calls `GET /fundamentals` with symbols and returns a list of `Fundamental` entities.
If `symbols` is not a string, it is concatenated with commas.

### REST.get_fundamental(symbol)
Calls `GET /assets/{symbol}/fundamental` and returns a `Fundamental` entity.

### REST.list_bars(symbols, timeframe, start_dt=None, end_dt=None, limit=None)
Calls `GET /bars` and returns a list of `AssetBars` entities. If `symbols` is
not a string, it is concatenated with commas. `start_dt` and `end_dt` should be
in the ISO8601 string format.

### REST.get_bars(symbol, timeframe, start_dt=None, end_dt=None, limit=None)
Calls `GET /assets/{symbol}/bars` with parameters and returns an `AssetBars`
entity.  `start_dt` and `end_dt` should be in the ISO8601 string format.


## StreamConn

The `StreamConn` class provides WebSocket-based event-driven
interfaces.  Using the `on` decorator of the instance, you can
define custom event handlers that are called when the pattern
is matched on the stream name.  Once event handlers are set up,
call the `run` method which runs forever until a critical exception
is raised. This module itself does not provide any threading
capability, so if you need to consume the messages pushed from the
server, you need to run it in a background thread.

The `run` method routine starts from establishing the WebSocket
connection, immediately followed by the authentication
handshake. The `authenticated` event is called right after authentication
is done, where it is the best time to start subscribing to particular
streams you are interested in, by calling the `subscribe` method.

The `run` method tries to reconnect to the server in the event of
connection failure.  In this case you may want to reset your state
which is best in the `connect` event.  The method still raises
exception in the case any other unknown error happens inside the
event loop.

The `msg` object passed to each handler is wrapped by the entity
helper class if the message is from the server.

```python
@conn.on(r'quotes/')
def on_quotes(conn, stream, quote):
    print('quotes', quote)

```

You will likely call the `run` method in a thread since it will keep runnig
unless an exception is raised.

### StreamConn.subscribe(streams)
Request "listen" to the server.  `streams` must be a list of string stream names.
A "listening" response will be triggered if server responses to this request.

### StreamConn.run()
Goes into an infinite loop and awaits for messages from the server.  You should
set up event listeners using the `on` or `register` method before calling `run`.

### StreamConn.on(stream_pat)
As in the above example, this is a decorator method to add an event handler function.
`stream_pat` is used as a regular expression pattern to filter stream names.

### StreamConn.register(stream_pat, func)
Registers a function as an event handler that is triggered by the stream events
that match with `stream_path` regular expression. Calling this method with the
same `stream_pat` will overwrite the old handler.

### StreamConn.deregister(stream_pat)
Deregisters the event handler function that was previously registered via `on` or
`register` method.


## Support and Contribution

For technical issues particular to this module, please report the
issue on this GitHub repository. Any API issues can be reported through
Alpaca's customer support.

New features, as well as bug fixes, by sending pull request is always
welcomed.
