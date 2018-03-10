import alpy

import pytest
import requests_mock


@pytest.fixture
def reqmock():
    with requests_mock.Mocker() as m:
        yield m


@pytest.fixture
def account():
    api = alpy.API('test_key')
    return alpy.api.Account({
        "id": "904837e3-3b76-47ec-b432-046db621571b",
        "status": "ONBOARDING",
        "currency": "USD",
        "amount_tradable": "4000.32",
        "amount_withdrawable": "4000.32",
        "plan": "REGULAR",
        "pattern_day_trader": True,
        "trading_blocked": True,
        "transfers_blocked": True,
        "account_blocked": True,
        "created_at": "2018-03-09T05:50:50Z",
        "updated_at": "2018-03-09T05:50:50Z"
    }, api)


def test_list_accounts(reqmock):
    reqmock.get('https://api.alpaca.markets/api/v1/accounts', text='''
    [
      {
        "id": "904837e3-3b76-47ec-b432-046db621571b",
        "status": "ONBOARDING",
        "currency": "USD",
        "amount_tradable": "4000.32",
        "amount_withdrawable": "4000.32",
        "plan": "REGULAR",
        "pattern_day_trader": true,
        "trading_blocked": true,
        "transfers_blocked": true,
        "account_blocked": true,
        "created_at": "2018-03-09T05:50:50Z",
        "updated_at": "2018-03-09T05:50:50Z"
      }
    ]
''')

    api = alpy.API('test-key')
    accounts = api.list_accounts()
    assert accounts[0].status == 'ONBOARDING'


def test_assets(reqmock):
    api = alpy.API('test-key')
    reqmock.get('https://api.alpaca.markets/api/v1/assets', text='''[
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

    asset_id = '904837e3-3b76-47ec-b432-046db621571b'
    reqmock.get('https://api.alpaca.markets/api/v1/assets/{}'.format(asset_id),
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


def test_orders(reqmock, account):
    # Get a list of orders
    reqmock.get(
        'https://api.alpaca.markets/api/v1/accounts/{}/orders'.format(
            account.id,
        ),
        text='''[
  {
    "id": "904837e3-3b76-47ec-b432-046db621571b",
    "client_order_id": "904837e3-3b76-47ec-b432-046db621571b",
    "account_id": "904837e3-3b76-47ec-b432-046db621571b",
    "asset_id": "904837e3-3b76-47ec-b432-046db621571b",
    "shares": 15,
    "side": "buy",
    "type": "market",
    "timeinforce": "day",
    "limit_price": "107.00",
    "stop_price": "106.00",
    "filled_price": "107.00",
    "status": "ordering",
    "created_at": "2018-03-09T19:05:27Z",
    "updated_at": "2018-03-09T19:05:27Z",
    "cancelled_at": "2018-03-09T19:05:27Z",
    "expired_at": "2018-03-09T19:05:27Z",
    "filled_at": "2018-03-09T19:05:27Z",
    "failed_at": "2018-03-09T19:05:27Z",
    "filled_shares": 0,
    "failured_reason": "string",
    "cancel_requested_at": "2018-03-09T19:05:27Z",
    "submitted_at": "2018-03-09T19:05:27Z"
  }
]''')
    orders = account.list_orders()
    assert orders[0].type == 'market'

    # Create an order
    reqmock.post(
        'https://api.alpaca.markets/api/v1/accounts/{}/orders'.format(
            account.id,
        ),
        text='''{
  "id": "904837e3-3b76-47ec-b432-046db621571b",
  "client_order_id": "904837e3-3b76-47ec-b432-046db621571b",
  "account_id": "904837e3-3b76-47ec-b432-046db621571b",
  "asset_id": "904837e3-3b76-47ec-b432-046db621571b",
  "shares": 15,
  "side": "buy",
  "type": "market",
  "timeinforce": "day",
  "limit_price": "107.00",
  "stop_price": "106.00",
  "filled_price": "107.00",
  "status": "ordering",
  "created_at": "2018-03-09T19:05:27Z",
  "updated_at": "2018-03-09T19:05:27Z",
  "cancelled_at": "2018-03-09T19:05:27Z",
  "expired_at": "2018-03-09T19:05:27Z",
  "filled_at": "2018-03-09T19:05:27Z",
  "failed_at": "2018-03-09T19:05:27Z",
  "filled_shares": 0,
  "failured_reason": "string",
  "cancel_requested_at": "2018-03-09T19:05:27Z",
  "submitted_at": "2018-03-09T19:05:27Z"
}''')
    order = account.create_order(
        asset_id='904837e3-3b76-47ec-b432-046db621571b',
        shares=15,
        side='buy',
        type='market',
        timeinforce='day',
        limit_price='107.00',
        stop_price='106.00',
    )
    assert order.shares == 15
    assert order.created_at.hour == 19

    # Get an order by client order id
    client_order_id = 'client-order-id'
    reqmock.get(
        ('https://api.alpaca.markets/api/v1/accounts/{}'
         '/orders?client_order_id={}').format(
            account.id, client_order_id,
        ),
        text='''{
  "id": "904837e3-3b76-47ec-b432-046db621571b",
  "client_order_id": "904837e3-3b76-47ec-b432-046db621571b",
  "account_id": "904837e3-3b76-47ec-b432-046db621571b",
  "asset_id": "904837e3-3b76-47ec-b432-046db621571b",
  "shares": 15,
  "side": "buy",
  "type": "market",
  "timeinforce": "day",
  "limit_price": "107.00",
  "stop_price": "106.00",
  "filled_price": "107.00",
  "status": "ordering",
  "created_at": "2018-03-09T05:50:50Z",
  "updated_at": "2018-03-09T05:50:50Z",
  "cancelled_at": "2018-03-09T05:50:50Z",
  "expired_at": "2018-03-09T05:50:50Z",
  "filled_at": "2018-03-09T05:50:50Z",
  "failed_at": "2018-03-09T05:50:50Z",
  "filled_shares": 0,
  "failured_reason": "string",
  "cancel_requested_at": "2018-03-09T05:50:50Z",
  "submitted_at": "2018-03-09T05:50:50Z"
}'''
    )
    order = account.get_order_by_client_order_id(client_order_id)
    assert order.submitted_at.minute == 50

    # Get an order
    order_id = '904837e3-3b76-47ec-b432-046db621571b'
    reqmock.get(
        'https://api.alpaca.markets/api/v1/accounts/{}/orders/{}'.format(
            account.id, order_id,
        ),
        text='''{
  "id": "904837e3-3b76-47ec-b432-046db621571b",
  "client_order_id": "904837e3-3b76-47ec-b432-046db621571b",
  "account_id": "904837e3-3b76-47ec-b432-046db621571b",
  "asset_id": "904837e3-3b76-47ec-b432-046db621571b",
  "shares": 15,
  "side": "buy",
  "type": "market",
  "timeinforce": "day",
  "limit_price": "107.00",
  "stop_price": "106.00",
  "filled_price": "107.00",
  "status": "ordering",
  "created_at": "2018-03-09T05:50:50Z",
  "updated_at": "2018-03-09T05:50:50Z",
  "cancelled_at": "2018-03-09T05:50:50Z",
  "expired_at": "2018-03-09T05:50:50Z",
  "filled_at": "2018-03-09T05:50:50Z",
  "failed_at": "2018-03-09T05:50:50Z",
  "filled_shares": 0,
  "failured_reason": "string",
  "cancel_requested_at": "2018-03-09T05:50:50Z",
  "submitted_at": "2018-03-09T05:50:50Z"
}'''
    )
    order = account.get_order(order_id)
    assert order.side == 'buy'

    # Cancel an order
    order_id = '904837e3-3b76-47ec-b432-046db621571b'
    reqmock.delete(
        'https://api.alpaca.markets/api/v1/accounts/{}/orders/{}'.format(
            account.id, order_id,
        ),
        text='',
        status_code=204,
    )
    account.delete_order(order_id)


def test_positions(reqmock, account):
    # Get a list of positions
    reqmock.get(
        'https://api.alpaca.markets/api/v1/accounts/{}/positions'.format(
            account.id,
        ),
        text='''[
  {
    "account_id": "904837e3-3b76-47ec-b432-046db621571b",
    "asset_id": "904837e3-3b76-47ec-b432-046db621571b",
    "entry_price": "100.0",
    "shares": 5,
    "side": "long",
    "market_value": "600.0",
    "cost_basis": "500.0",
    "last_price": "120.00"
  }
]'''
    )
    positions = account.list_positions()
    assert positions[0].entry_price == '100.0'

    # Get an open position
    asset_id = 'test-asset'
    reqmock.get(
        'https://api.alpaca.markets/api/v1/accounts/{}/positions/{}'.format(
            account.id, asset_id,
        ),
        text='''{
  "account_id": "904837e3-3b76-47ec-b432-046db621571b",
  "asset_id": "904837e3-3b76-47ec-b432-046db621571b",
  "entry_price": "100.0",
  "shares": 5,
  "side": "long",
  "market_value": "600.0",
  "cost_basis": "500.0",
  "last_price": "120.00"
}'''
    )
    position = account.get_position(asset_id)
    assert position.cost_basis == '500.0'
