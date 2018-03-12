import alpaca_trade_api as tradeapi

import pytest
import requests_mock


@pytest.fixture
def reqmock():
    with requests_mock.Mocker() as m:
        yield m


@pytest.fixture
def account():
    api = tradeapi.REST('test-key')
    return tradeapi.rest.Account({
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


@pytest.fixture
def asset():
    api = tradeapi.REST('test-key')
    return tradeapi.rest.Asset({
        "id": "904837e3-3b76-47ec-b432-046db621571b",
        "name": "Apple inc.",
        "asset_class": "us_equity",
        "exchange": "NASDAQ",
        "symbol": "AAPL",
        "status": "active",
        "tradable": True
    }, api)


def test_api(reqmock):
    api = tradeapi.REST('test-key')

    # Get a list of accounts
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

    accounts = api.list_accounts()
    assert accounts[0].status == 'ONBOARDING'

    # Get a list of assets
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

    # Get an asset
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

    # Get a list of quotes
    asset_ids = 'asset_1,asset_2'
    reqmock.get('https://api.alpaca.markets/api/v1/quotes?asset_ids={}'.format(
        asset_ids,
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
    quotes = api.list_quotes(asset_ids)
    assert quotes[0].ask == 120.4

    # Get a list of undamentals
    reqmock.get(
        'https://api.alpaca.markets/api/v1/fundamentals?asset_ids={}'.format(
            asset_ids, ), text='''[
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
    fundamentals = api.list_fundamentals(asset_ids)
    assert fundamentals[0].full_name == 'Apple inc.'


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


def test_assets(reqmock, asset):
    # Candles
    reqmock.get(
        'https://api.alpaca.markets/api/v1/assets/{}/candles'.format(
            asset.id,
        ),
        text='''[
  {
    "open": 120.4,
    "high": 120.5,
    "low": 120.4,
    "close": 120.45,
    "volume": 130000,
    "timestamp": "2018-04-01T12:00:00.000Z"
  }
]''',
    )
    candles = asset.list_candles()
    assert candles[0].open == 120.4

    # Quote
    reqmock.get(
        'https://api.alpaca.markets/api/v1/assets/{}/quote'.format(
            asset.id,
        ),
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
    quote = asset.get_quote()
    assert quote.last_timestamp.minute == 16

    # Fundamental
    reqmock.get(
        'https://api.alpaca.markets/api/v1/assets/{}/fundamental'.format(
            asset.id,
        ),
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
    fundamental = asset.get_fundamental()
    assert fundamental.pe_ratio == 17.42
