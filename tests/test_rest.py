import alpaca_trade_api as tradeapi

import os
import pytest
import requests_mock


if 'APCA_API_BASE_URL' in os.environ:
    del os.environ['APCA_API_BASE_URL']


@pytest.fixture
def reqmock():
    with requests_mock.Mocker() as m:
        yield m


def test_api(reqmock):
    api = tradeapi.REST('key-id', 'secret-key')

    # Get a list of accounts
    reqmock.get('https://api.alpaca.markets/v1/account', text='''
    {
      "id": "904837e3-3b76-47ec-b432-046db621571b",
      "status": "ACTIVE",
      "currency": "USD",
      "cash": "4000.32",
      "cash_withdrawable": "4000.32",
      "portfolio_value": "4321.98",
      "pattern_day_trader": false,
      "trading_blocked": false,
      "transfers_blocked": false,
      "account_blocked": false,
      "created_at": "2018-05-03T06:17:56Z"
    }
''')

    account = api.get_account()
    assert account.status == 'ACTIVE'

    # Get a list of assets
    reqmock.get('https://api.alpaca.markets/v1/assets', text='''[
  {
    "id": "904837e3-3b76-47ec-b432-046db621571b",
    "name": "Apple inc.",
    "asset_class": "us_equity",
    "exchange": "NASDAQ",
    "symbol": "AAPL",
    "status": "active",
    "tradable": true
  }
]''')
    assets = api.list_assets()
    assert assets[0].name == 'Apple inc.'

    # Get an asset
    asset_id = '904837e3-3b76-47ec-b432-046db621571b'
    reqmock.get('https://api.alpaca.markets/v1/assets/{}'.format(asset_id),
                text='''{
    "id": "904837e3-3b76-47ec-b432-046db621571b",
    "name": "Apple inc.",
    "asset_class": "us_equity",
    "exchange": "NASDAQ",
    "symbol": "AAPL",
    "status": "active",
    "tradable": true
  }''')
    asset = api.get_asset(asset_id)
    assert asset.name == 'Apple inc.'

    # Get a list of quotes
    symbols = 'asset_1,asset_2'
    reqmock.get('https://api.alpaca.markets/v1/quotes?symbols={}'.format(
        symbols,
    ),
        text='''[
  {
    "asset_id": "904837e3-3b76-47ec-b432-046db621571b",
    "bid": 120.4,
    "bid_timestamp": "2018-02-28T21:16:58.704+0000",
    "ask": 120.4,
    "ask_timestamp": "2018-02-28T21:16:58.704+0000",
    "last": 120.4,
    "last_timestamp": "2018-02-28T21:16:58.704+0000",
    "day_change": 0.008050799
  }
]''')
    quotes = api.list_quotes(symbols)
    assert quotes[0].ask == 120.4

    # Get a list of fundamentals
    reqmock.get(
        'https://api.alpaca.markets/v1/fundamentals?symbols={}'.format(
            symbols,
        ), text='''[
  {
    "symbol": "string",
    "asset_id": "904837e3-3b76-47ec-b432-046db621571b",
    "full_name": "Apple inc.",
    "industry_name": "Electronic Equipment",
    "sector": "Consumer Goods",
    "pe_ratio": 17.42,
    "peg_ratio": 1.49,
    "beta": 1.21,
    "eps": 10.22,
    "market_cap": 910710000000,
    "shares_outstanding": 5110000000,
    "avg_vol": 35330000,
    "ex_div_date": "2017/12/12",
    "div_rate": 1.41,
    "roa": 13.8,
    "roe": 37.4,
    "roi": 18.3,
    "ps": 3.81,
    "pc": 11.8,
    "gross_margin": 38.4
  }
]''')
    fundamentals = api.list_fundamentals(symbols)
    assert fundamentals[0].full_name == 'Apple inc.'


def test_orders(reqmock):
    api = tradeapi.REST('key-id', 'secret-key')

    # Get a list of orders
    reqmock.get(
        'https://api.alpaca.markets/v1/orders',
        text='''[
  {
    "id": "904837e3-3b76-47ec-b432-046db621571b",
    "client_order_id": "904837e3-3b76-47ec-b432-046db621571b",
    "account_id": "904837e3-3b76-47ec-b432-046db621571b",
    "asset_id": "904837e3-3b76-47ec-b432-046db621571b",
    "qty": "15",
    "side": "buy",
    "type": "market",
    "timeinforce": "day",
    "limit_price": "107.00",
    "stop_price": "106.00",
    "filled_avg_price": "107.00",
    "status": "new",
    "created_at": "2018-03-09T19:05:27Z",
    "updated_at": "2018-03-09T19:05:27Z",
    "cancelled_at": "2018-03-09T19:05:27Z",
    "expired_at": "2018-03-09T19:05:27Z",
    "filled_at": "2018-03-09T19:05:27Z",
    "failed_at": "2018-03-09T19:05:27Z",
    "filled_qty": "0",
    "failured_reason": "string",
    "cancel_requested_at": "2018-03-09T19:05:27Z",
    "submitted_at": "2018-03-09T19:05:27Z"
  }
]''')
    orders = api.list_orders()
    assert orders[0].type == 'market'

    # Create an order
    reqmock.post(
        'https://api.alpaca.markets/v1/orders',
        text='''{
  "id": "904837e3-3b76-47ec-b432-046db621571b",
  "client_order_id": "904837e3-3b76-47ec-b432-046db621571b",
  "account_id": "904837e3-3b76-47ec-b432-046db621571b",
  "asset_id": "904837e3-3b76-47ec-b432-046db621571b",
  "qty": "15",
  "side": "buy",
  "type": "market",
  "timeinforce": "day",
  "limit_price": "107.00",
  "stop_price": "106.00",
  "filled_avg_price": "107.00",
  "status": "new",
  "created_at": "2018-03-09T19:05:27Z",
  "updated_at": "2018-03-09T19:05:27Z",
  "cancelled_at": "2018-03-09T19:05:27Z",
  "expired_at": "2018-03-09T19:05:27Z",
  "filled_at": "2018-03-09T19:05:27Z",
  "failed_at": "2018-03-09T19:05:27Z",
  "filled_qty": "0",
  "failured_reason": "string",
  "cancel_requested_at": "2018-03-09T19:05:27Z",
  "submitted_at": "2018-03-09T19:05:27Z"
}''')
    order = api.submit_order(
        symbol='904837e3-3b76-47ec-b432-046db621571b',
        qty=15,
        side='buy',
        type='market',
        time_in_force='day',
        limit_price='107.00',
        stop_price='106.00',
    )
    assert order.qty == "15"
    assert order.created_at.hour == 19

    # Get an order by client order id
    client_order_id = 'client-order-id'
    reqmock.get(
        'https://api.alpaca.markets/v1/orders:by_client_order_id?'
        'client_order_id={}'.format(
            client_order_id, ), text='''{
  "id": "904837e3-3b76-47ec-b432-046db621571b",
  "client_order_id": "904837e3-3b76-47ec-b432-046db621571b",
  "account_id": "904837e3-3b76-47ec-b432-046db621571b",
  "asset_id": "904837e3-3b76-47ec-b432-046db621571b",
  "qty": "15",
  "side": "buy",
  "type": "market",
  "timeinforce": "day",
  "limit_price": "107.00",
  "stop_price": "106.00",
  "filled_avg_price": "107.00",
  "status": "new",
  "created_at": "2018-03-09T05:50:50Z",
  "updated_at": "2018-03-09T05:50:50Z",
  "cancelled_at": "2018-03-09T05:50:50Z",
  "expired_at": "2018-03-09T05:50:50Z",
  "filled_at": "2018-03-09T05:50:50Z",
  "failed_at": "2018-03-09T05:50:50Z",
  "filled_qty": "0",
  "failured_reason": "string",
  "cancel_requested_at": "2018-03-09T05:50:50Z",
  "submitted_at": "2018-03-09T05:50:50Z"
}''')
    order = api.get_order_by_client_order_id(client_order_id)
    assert order.submitted_at.minute == 50

    # Get an order
    order_id = '904837e3-3b76-47ec-b432-046db621571b'
    reqmock.get(
        'https://api.alpaca.markets/v1/orders/{}'.format(order_id),
        text='''{
  "id": "904837e3-3b76-47ec-b432-046db621571b",
  "client_order_id": "904837e3-3b76-47ec-b432-046db621571b",
  "account_id": "904837e3-3b76-47ec-b432-046db621571b",
  "asset_id": "904837e3-3b76-47ec-b432-046db621571b",
  "qty": 15,
  "side": "buy",
  "type": "market",
  "timeinforce": "day",
  "limit_price": "107.00",
  "stop_price": "106.00",
  "filled_avg_price": "107.00",
  "status": "new",
  "created_at": "2018-03-09T05:50:50Z",
  "updated_at": "2018-03-09T05:50:50Z",
  "cancelled_at": "2018-03-09T05:50:50Z",
  "expired_at": "2018-03-09T05:50:50Z",
  "filled_at": "2018-03-09T05:50:50Z",
  "failed_at": "2018-03-09T05:50:50Z",
  "filled_qty": "0",
  "failured_reason": "string",
  "cancel_requested_at": "2018-03-09T05:50:50Z",
  "submitted_at": "2018-03-09T05:50:50Z"
}'''
    )
    order = api.get_order(order_id)
    assert order.side == 'buy'

    # Cancel an order
    order_id = '904837e3-3b76-47ec-b432-046db621571b'
    reqmock.delete(
        'https://api.alpaca.markets/v1/orders/{}'.format(order_id),
        text='',
        status_code=204,
    )
    api.cancel_order(order_id)


def test_positions(reqmock):
    api = tradeapi.REST('key-id', 'secret-key')

    # Get a list of positions
    reqmock.get(
        'https://api.alpaca.markets/v1/positions',
        text='''[
  {
    "account_id": "904837e3-3b76-47ec-b432-046db621571b",
    "asset_id": "904837e3-3b76-47ec-b432-046db621571b",
    "entry_price": "100.0",
    "qty": "5",
    "side": "long",
    "market_value": "600.0",
    "cost_basis": "500.0",
    "last_price": "120.00"
  }
]'''
    )
    positions = api.list_positions()
    assert positions[0].entry_price == '100.0'

    # Get an open position
    asset_id = 'test-asset'
    reqmock.get(
        'https://api.alpaca.markets/v1/positions/{}'.format(asset_id),
        text='''{
  "account_id": "904837e3-3b76-47ec-b432-046db621571b",
  "asset_id": "904837e3-3b76-47ec-b432-046db621571b",
  "entry_price": "100.0",
  "qty": "5",
  "side": "long",
  "market_value": "600.0",
  "cost_basis": "500.0",
  "last_price": "120.00"
}'''
    )
    position = api.get_position(asset_id)
    assert position.cost_basis == '500.0'


def test_chronos(reqmock):
    api = tradeapi.REST('key-id', 'secret-key')

    # clock
    reqmock.get(
        'https://api.alpaca.markets/v1/clock',
        text='''{
  "timestamp": "2018-04-01T12:00:00.000Z",
  "is_open": true,
  "next_open": "2018-04-01T12:00:00.000Z",
  "next_close": "2018-04-01T12:00:00.000Z"
}'''
    )
    clock = api.get_clock()
    assert clock.is_open
    assert clock.next_open.day == 1

    # calendar
    reqmock.get(
        'https://api.alpaca.markets/v1/calendar?start=2018-01-03',
        text='''[
  {
    "date": "2018-01-03",
    "open": "09:30",
    "close": "16:00"
  }
]'''
    )
    calendar = api.get_calendar(start='2018-01-03')
    assert calendar[0].date.day == 3
    assert calendar[0].open.minute == 30


def test_assets(reqmock):
    api = tradeapi.REST('key-id', 'secret-key')
    # Bars
    reqmock.get(
        'https://api.alpaca.markets/v1/assets/AAPL/bars?timeframe=1D',
        text='''{
  "asset_id": "904837e3-3b76-47ec-b432-046db621571b",
  "symbol": "AAPL",
  "exchange": "NASDAQ",
  "asset_class": "us_equity",
  "bars": [
    {
      "open": 120.4,
      "high": 120.4,
      "low": 120.4,
      "close": 120.4,
      "volume": 1000,
      "time": "2018-04-01T12:00:00.000Z"
    }
  ]
}''',
    )
    abars = api.get_bars('AAPL', '1D')
    assert abars.bars[0].open == 120.4
    assert abars.df.shape == (1, 5)
    assert abars.df.index[0].day == 1

    # Quote
    reqmock.get(
        'https://api.alpaca.markets/v1/assets/AAPL/quote',
        text='''{
  "asset_id": "904837e3-3b76-47ec-b432-046db621571b",
  "bid": 120.4,
  "bid_timestamp": "2018-02-28T21:16:58.704+0000",
  "ask": 120.4,
  "ask_timestamp": "2018-02-28T21:16:58.704+0000",
  "last": 120.4,
  "last_timestamp": "2018-02-28T21:16:58.704+0000",
  "day_change": 0.008050799
}''',
    )
    quote = api.get_quote('AAPL')
    assert quote.last_timestamp.minute == 16

    # Fundamental
    reqmock.get(
        'https://api.alpaca.markets/v1/assets/AAPL/fundamental',
        text='''{
  "symbol": "string",
  "asset_id": "904837e3-3b76-47ec-b432-046db621571b",
  "full_name": "Apple inc.",
  "industry_name": "Electronic Equipment",
  "sector": "Consumer Goods",
  "pe_ratio": 17.42,
  "peg_ratio": 1.49,
  "beta": 1.21,
  "eps": 10.22,
  "market_cap": 910710000000,
  "shares_outstanding": 5110000000,
  "avg_vol": 35330000,
  "ex_div_date": "2017/12/12",
  "div_rate": 1.41,
  "roa": 13.8,
  "roe": 37.4,
  "roi": 18.3,
  "ps": 3.81,
  "pc": 11.8,
  "gross_margin": 38.4
}''',
    )
    fundamental = api.get_fundamental('AAPL')
    assert fundamental.pe_ratio == 17.42
