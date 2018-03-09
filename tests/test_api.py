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

    api = alpy.API('test_key')
    accounts = api.list_accounts()
    assert accounts[0].status == 'ONBOARDING'


def test_orders(reqmock, account):
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
        assert_id='904837e3-3b76-47ec-b432-046db621571b',
        shares=15,
        side='buy',
        type='market',
        timeinforce='day',
        limit_price='107.00',
        stop_price='106.00',
    )
    assert order.shares == 15
    assert order.created_at.hour == 19
