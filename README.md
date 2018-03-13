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
account = api.list_accounts()[0]
account.list_positions()
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
        'bars/bats/AAPL/1Min',
        'quotes/gdax/BTC-USD',
        ])

@conn.on(r'bars/')
def on_bars(conn, stream, msg):
    print('bars', msg)

@conn.on(r'account_updates')
def on_account(conn, stream, msg):
    print('account', msg)

# blocks forever
conn.run()
```

## Authentication

The API requires API key ID and secret key, which you can obtain from the
web console after you sign in.  You can give them to the initializers of
`REST` or `StreamConn` as arguments, or set up environment variables as
follows.

- APCA_API_KEY_ID: key ID
- APCA_API_SECRET_KEY: secret key

## REST

The `REST` class is the entry point for the API request.  Call
`list_accounts` to obtain Account Entity with which you can further
query the up-to-date information of orders and positions under the
particular account.

For the market data, you can directly request bars, quotes and
fundamentals from the same instance of `REST`.

## Streaming

The `Streaming` class provides WebSocket-based event-driven
interfaces.  Using the `on` decorator of the instance, you can
define custom event handlers that are called when the pattern
is matched on the stream name.  Once event handlers are set up,
call the `run` method which runs forever until critical exception
is raised. This module itself does not provide any threading
capability, so if you need to consume the messages pushed from the
server, you need to run it in a background thread.

The `run` method routine starts from establishing the WebSocket
connection, which is immediately followed by the authentication
handshake. The `authenticated` event is called right after authentication
is done, where it is the best time to start subscribing to particular
streams you are interested in, by calling the `subscribe` method.

The `run` method tries to reconnect to the server in the event of
connection failure.  In this case you may want to reset your state
which is best in the `connect` event.  The method still raises
exception in the case any other unknown error happens inside the
event loop.


## Support and Contribute

For technical issues particular to this module, please report the
issue on this GitHub repository. Any API issue can be reported through
Alpaca's customer support.

New features, as well as bug fixes by sending pull request is always
welcomed.
