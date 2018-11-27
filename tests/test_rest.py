import alpaca_trade_api as tradeapi
from alpaca_trade_api.rest import APIError

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
    assert 'Account(' in str(account)

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
    orders = api.list_orders('all')
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
        client_order_id='904837e3-3b76-47ec-b432-046db621571b',
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


def test_data(reqmock):
    api = tradeapi.REST('key-id', 'secret-key')
    # Bars
    reqmock.get(
        'https://data.alpaca.markets/v1/bars/1D?symbols=AAPL,TSLA&limit=2',
        text='''
        {   "AAPL": [   {   "c": 172.29,
                    "h": 176.595,
                    "l": 172.1,
                    "o": 174.94,
                    "t": 1542949200,
                    "v": 23623972},
                {   "c": 174.62,
                    "h": 174.95,
                    "l": 170.26,
                    "o": 174.24,
                    "t": 1543208400,
                    "v": 44998520}],
            "TSLA": [   {   "c": 325.83,
                    "h": 337.5,
                    "l": 325.55,
                    "o": 334.345,
                    "t": 1542949200,
                    "v": 4202642},
                {   "c": 346,
                    "h": 346.22,
                    "l": 325,
                    "o": 325,
                    "t": 1543208400,
                    "v": 7992141}]}''',
    )
    barset = api.get_barset('AAPL,TSLA', '1D', limit=2)
    assert barset['AAPL'][0].o == 174.94
    assert barset['TSLA'][1].h == 346.22
    assert barset['AAPL'][0].t.day == 23
    assert barset['AAPL'].df.index[0].day == 23


def test_errors(reqmock):
    api = tradeapi.REST('key-id', 'secret-key')

    api._retry = 1
    api._retry_wait = 0

    api._do_error = True

    def callback_429(request, context):
        if api._do_error:
            api._do_error = False
            context.status_code = 429
            return 'Too Many Requests'
        else:
            context.status_code = 200
            return '''
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
'''
    # Too Many Requests
    reqmock.get(
        'https://api.alpaca.markets/v1/account',
        text=callback_429,
    )

    account = api.get_account()
    assert account.cash == '4000.32'

    # General API Error
    reqmock.post(
        'https://api.alpaca.markets/v1/orders',
        status_code=403,
        text='''
    {"code": 10041, "message": "Order failed"}
'''
    )

    try:
        api.submit_order(
            symbol='AAPL',
            side='buy',
            qty='3',
            type='market',
            time_in_force='day',
        )
    except APIError as err:
        assert err.code == 10041
        assert err.status_code == 403
        assert err.request is not None
        assert err.response.status_code == err.status_code
    else:
        assert False
