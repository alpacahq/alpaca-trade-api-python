import alpaca_trade_api as tradeapi
from alpaca_trade_api.rest import APIError

import os
import pytest
import requests_mock


@pytest.fixture(autouse=True)
def delete_base_url_envs():
    if 'APCA_API_BASE_URL' in os.environ:
        del os.environ['APCA_API_BASE_URL']
    if 'APCA_API_DATA_URL' in os.environ:
        del os.environ['APCA_API_DATA_URL']


@pytest.fixture
def reqmock():
    with requests_mock.Mocker() as m:
        yield m


def test_api(reqmock):
    api = tradeapi.REST('key-id', 'secret-key', api_version='v1')
    api_raw = tradeapi.REST('key-id', 'secret-key', api_version='v1',
                            raw_data=True)

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
    assert type(account) == tradeapi.entity.Account
    assert type(api_raw.get_account()) == dict

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
    assert type(assets[0]) == tradeapi.entity.Asset
    assert type(api_raw.list_assets()) == list

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
    assert type(asset) == tradeapi.entity.Asset
    assert type(api_raw.get_asset(asset_id)) == dict


def test_orders(reqmock):
    api = tradeapi.REST('key-id', 'secret-key', api_version='v1')
    api_raw = tradeapi.REST('key-id', 'secret-key', api_version='v1',
                            raw_data=True)

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
    "hwm": null,
    "trail_percent": null,
    "trail_price": null,
    "failured_reason": "string",
    "cancel_requested_at": "2018-03-09T19:05:27Z",
    "submitted_at": "2018-03-09T19:05:27Z"
  }
]''')
    orders = api.list_orders('all')
    assert orders[0].type == 'market'
    assert type(orders[0]) == tradeapi.entity.Order
    assert type(api_raw.list_orders()) == list

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
  "hwm": null,
  "trail_percent": null,
  "trail_price": null,
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
    assert type(order) == tradeapi.entity.Order
    assert type(api_raw.submit_order(
        symbol='904837e3-3b76-47ec-b432-046db621571b',
        qty=15,
        side='buy',
        type='market',
        time_in_force='day',
        limit_price='107.00',
        stop_price='106.00',
        client_order_id='904837e3-3b76-47ec-b432-046db621571b',)) == dict
    # now let's test some different acceptable "float" formats
    api.submit_order(
        symbol='904837e3-3b76-47ec-b432-046db621571b',
        qty=15,
        side='buy',
        type='market',
        time_in_force='day',
        limit_price='107.00',  # str float
        stop_price=106.00,  # float
        client_order_id='904837e3-3b76-47ec-b432-046db621571b',
    )
    api.submit_order(
        symbol='904837e3-3b76-47ec-b432-046db621571b',
        qty=15,
        side='buy',
        type='market',
        time_in_force='day',
        limit_price='107.00',  # str float
        stop_price=106,  # int
        client_order_id='904837e3-3b76-47ec-b432-046db621571b',
    )
    with pytest.raises(ValueError):
        api.submit_order(
            symbol='904837e3-3b76-47ec-b432-046db621571b',
            qty=15,
            side='buy',
            type='market',
            time_in_force='day',
            limit_price='1',
            stop_price="a",
            client_order_id='904837e3-3b76-47ec-b432-046db621571b',
        )
    with pytest.raises(ValueError):
        api.submit_order(
            symbol='904837e3-3b76-47ec-b432-046db621571b',
            qty=15,
            side='buy',
            type='market',
            time_in_force='day',
            limit_price='a',
            stop_price=106.00,
            client_order_id='904837e3-3b76-47ec-b432-046db621571b',
        )

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
  "hwm": null,
  "trail_percent": null,
  "trail_price": null,
  "failured_reason": "string",
  "cancel_requested_at": "2018-03-09T05:50:50Z",
  "submitted_at": "2018-03-09T05:50:50Z"
}''')
    order = api.get_order_by_client_order_id(client_order_id)
    assert order.submitted_at.minute == 50
    assert type(order) == tradeapi.entity.Order
    assert type(api_raw.get_order_by_client_order_id(client_order_id)) == dict

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
  "hwm": null,
  "trail_percent": null,
  "trail_price": null,
  "failured_reason": "string",
  "cancel_requested_at": "2018-03-09T05:50:50Z",
  "submitted_at": "2018-03-09T05:50:50Z"
}'''
    )
    order = api.get_order(order_id)
    assert order.side == 'buy'
    assert type(order) == tradeapi.entity.Order
    assert type(api_raw.get_order(order_id)) == dict

    # Cancel an order
    order_id = '904837e3-3b76-47ec-b432-046db621571b'
    reqmock.delete(
        'https://api.alpaca.markets/v1/orders/{}'.format(order_id),
        text='',
        status_code=204,
    )
    api.cancel_order(order_id)


def test_positions(reqmock):
    api = tradeapi.REST('key-id', 'secret-key', api_version='v1')
    api_raw = tradeapi.REST('key-id', 'secret-key', api_version='v1',
                            raw_data=True)

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
    assert type(positions[0]) == tradeapi.entity.Position
    assert type(api_raw.list_positions()) == list

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
    assert type(position) == tradeapi.entity.Position
    assert type(api_raw.get_position(asset_id)) == dict


def test_chronos(reqmock):
    api = tradeapi.REST('key-id', 'secret-key', api_version='v1')
    api_raw = tradeapi.REST('key-id', 'secret-key', api_version='v1',
                            raw_data=True)

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
    assert type(clock) == tradeapi.entity.Clock
    assert type(api_raw.get_clock()) == dict

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
    assert type(calendar) == list
    assert type(calendar[0]) == tradeapi.entity.Calendar
    assert type(api_raw.get_calendar(start='2018-01-03')) == list


def test_data(reqmock):
    api = tradeapi.REST('key-id', 'secret-key', api_version='v1')
    api_raw = tradeapi.REST('key-id', 'secret-key', api_version='v1',
                            raw_data=True)
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
    assert type(barset) == tradeapi.entity.BarSet
    assert type(api_raw.get_barset('AAPL,TSLA', '1D', limit=2)) == dict

    # Aggs
    reqmock.get(
        'https://data.alpaca.markets/v1/aggs/ticker/AAPL/'
        'range/1/day/2020-02-10/2020-02-12',
        text='''
        {
            "ticker": "AAPL",
            "status": "OK",
            "adjusted": true,
            "queryCount": 3,
            "resultsCount": 3,
            "results": [
                {
                    "v": 23748626,
                    "o": 314.18,
                    "c": 321.54,
                    "h": 321.54,
                    "l": 313.85,
                    "t": 1581310800000,
                    "n": 1
                },
                {
                    "v": 21107108,
                    "o": 323.6,
                    "c": 319.61,
                    "h": 323.9,
                    "l": 318.71,
                    "t": 1581397200000,
                    "n": 1
                },
                {
                    "v": 24425223,
                    "o": 321.62,
                    "c": 327.2,
                    "h": 327.21,
                    "l": 321.47,
                    "t": 1581483600000,
                    "n": 1
                }
            ]
        }'''
    )
    aggs = api.get_aggs('AAPL', 1, 'day', '2020-02-10', '2020-02-12')
    assert len(aggs) == 3
    assert aggs[0].open == 314.18
    assert aggs.df.iloc[1].high == 323.9
    assert type(aggs) == tradeapi.entity.Aggs
    assert type(api_raw.get_aggs(
        'AAPL', 1, 'day', '2020-02-10', '2020-02-12')) == dict
    with pytest.raises(AttributeError):
        aggs[2].foo

    # Last trade
    reqmock.get(
        'https://data.alpaca.markets/v1/last/stocks/AAPL',
        text='''
        {
            "status": "success",
            "symbol": "AAPL",
            "last": {
                "price": 159.59,
                "size": 20,
                "exchange": 11,
                "cond1": 14,
                "cond2": 16,
                "cond3": 0,
                "cond4": 0,
                "timestamp": 1518101436000900000
            }
        }
        '''
    )
    trade = api.get_last_trade('AAPL')
    assert trade.price == 159.59
    assert trade.timestamp.day == 8
    assert type(trade) == tradeapi.entity.Trade
    assert type(api_raw.get_last_trade('AAPL')) == dict

    # Last quote
    reqmock.get(
        'https://data.alpaca.markets/v1/last_quote/stocks/AAPL',
        text='''
        {
            "status": "success",
            "symbol": "AAPL",
            "last": {
                "askprice": 159.59,
                "asksize": 2,
                "askexchange": 11,
                "bidprice": 159.45,
                "bidsize": 20,
                "bidexchange": 12,
                "timestamp": 1518101436000900000
            }
        }'''
    )

    quote = api.get_last_quote('AAPL')
    assert quote.askprice == 159.59
    assert quote.timestamp.day == 8
    assert type(quote) == tradeapi.entity.Quote
    assert type(api_raw.get_last_quote('AAPL')) == dict


def test_watchlists(reqmock):
    api = tradeapi.REST('key-id', 'secret-key', api_version='v1')
    api_raw = tradeapi.REST('key-id', 'secret-key', api_version='v1',
                            raw_data=True)
    # get watchlists
    reqmock.get(
        'https://api.alpaca.markets/v1/watchlists',
        text='''[
    {
        "id": "900e20b1-46eb-492b-a505-2ea67386b5fd",
        "account_id": "1f893862-13b5-4603-b3ca-513980c00c6e",
        "created_at": "2019-10-31T01:45:41.308091Z",
        "updated_at": "2019-12-09T17:50:57.151693Z",
        "name": "Primary Watchlist"
    },
    {
        "id": "e65f2f2d-b596-4db6-bd68-1b7ceb77cccc",
        "account_id": "1f893862-13b5-4603-b3ca-513980c00c6e",
        "created_at": "2020-01-23T00:52:07.049138Z",
        "updated_at": "2020-01-23T00:57:27.063889Z",
        "name": "dev"
    },
    {
        "id": "e7574813-a853-4536-a52b-b47cc25def14",
        "account_id": "1f893862-13b5-4603-b3ca-513980c00c6e",
        "created_at": "2020-01-23T01:36:25.807997Z",
        "updated_at": "2020-01-23T01:36:25.807997Z",
        "name": "prod"
    }
    ]''')
    watchlists = api.get_watchlists()
    assert watchlists[0].name == 'Primary Watchlist'
    assert watchlists[1].id == 'e65f2f2d-b596-4db6-bd68-1b7ceb77cccc'
    assert watchlists[2].account_id == '1f893862-13b5-4603-b3ca-513980c00c6e'
    assert type(watchlists[0]) == tradeapi.entity.Watchlist
    assert type(api_raw.get_watchlists()) == list

    # get a watchlist by watchlist_id
    watchlist_id = "e65f2f2d-b596-4db6-bd68-1b7ceb77cccc"
    symbol = "AMD"
    reqmock.get(
        'https://api.alpaca.markets/v1/watchlists/{}'.format(watchlist_id),
        text='''{
            "id": "e65f2f2d-b596-4db6-bd68-1b7ceb77cccc",
            "account_id": "1f893862-13b5-4603-b3ca-513980c00c6e",
            "created_at": "2020-01-23T00:52:07.049138Z",
            "updated_at": "2020-01-23T00:57:27.063889Z",
            "name": "Primary Watchlist",
            "assets": [
        {
            "id": "03fb07bb-5db1-4077-8dea-5d711b272625",
            "class": "us_equity",
            "exchange": "NASDAQ",
            "symbol": "AMD",
            "name": "",
            "status": "active",
            "tradable": true,
            "marginable": true,
            "shortable": true,
            "easy_to_borrow": true
        },
        {
            "id": "4ce9353c-66d1-46c2-898f-fce867ab0247",
            "class": "us_equity",
            "exchange": "NASDAQ",
            "symbol": "NVDA",
            "name": "",
            "status": "active",
            "tradable": true,
            "marginable": true,
            "shortable": true,
            "easy_to_borrow": true
        },
        {
            "id": "bb2a26c0-4c77-4801-8afc-82e8142ac7b8",
            "class": "us_equity",
            "exchange": "NASDAQ",
            "symbol": "NFLX",
            "name": "",
            "status": "active",
            "tradable": true,
            "marginable": true,
            "shortable": true,
            "easy_to_borrow": true
        },
        {
            "id": "24cbba8c-831b-44e2-8503-dd0c2ed7af8f",
            "class": "us_equity",
            "exchange": "NASDAQ",
            "symbol": "PYPL",
            "name": "",
            "status": "active",
            "tradable": true,
            "marginable": true,
            "shortable": true,
            "easy_to_borrow": true
        }
    ]
    }''')
    watchlist = api.get_watchlist(watchlist_id)
    assert watchlist.name == 'Primary Watchlist'
    assert len(watchlist.assets) == 4
    assert watchlist.assets[0]["id"] == "03fb07bb-5db1-4077-8dea-5d711b272625"
    assert watchlist.assets[0]["class"] == "us_equity"
    assert watchlist.assets[0]["exchange"] == "NASDAQ"
    assert watchlist.assets[0]["symbol"] == "AMD"
    assert watchlist.assets[0]["name"] == ""
    assert watchlist.assets[0]["status"] == "active"
    assert watchlist.assets[0]["tradable"]
    assert watchlist.assets[0]["marginable"]
    assert watchlist.assets[0]["shortable"]
    assert watchlist.assets[0]["easy_to_borrow"]
    assert type(watchlist) == tradeapi.entity.Watchlist
    assert type(api_raw.get_watchlist(watchlist_id)) == dict

    # add an asset to a watchlist
    reqmock.post(
        'https://api.alpaca.markets/v1/watchlists/{}'.format(watchlist_id),
        text='''{
            "id": "e65f2f2d-b596-4db6-bd68-1b7ceb77cccc",
            "account_id": "1f893862-13b5-4603-b3ca-513980c00c6e",
            "created_at": "2020-01-23T00:52:07.049138Z",
            "updated_at": "2020-01-23T00:57:27.063889Z",
            "name": "Primary Watchlist",
            "assets": [
        {
            "id": "03fb07bb-5db1-4077-8dea-5d711b272625",
            "class": "us_equity",
            "exchange": "NASDAQ",
            "symbol": "AMD",
            "name": "",
            "status": "active",
            "tradable": true,
            "marginable": true,
            "shortable": true,
            "easy_to_borrow": true
        }
    ]
    }''')
    watchlist = api.add_to_watchlist(watchlist_id, symbol="AMD")
    assert watchlist.name == 'Primary Watchlist'
    assert len(watchlist.assets) == 1
    assert watchlist.assets[0]["symbol"] == "AMD"
    assert type(watchlist) == tradeapi.entity.Watchlist
    assert type(api_raw.add_to_watchlist(watchlist_id, symbol="AMD")) == dict

    # remove an item from a watchlist
    reqmock.delete(
        'https://api.alpaca.markets/v1/watchlists/{}/{}'.format(
            watchlist_id, symbol
        ),
        text='''{
    "id": "e65f2f2d-b596-4db6-bd68-1b7ceb77cccc",
    "account_id": "1f893862-13b5-4603-b3ca-513980c00c6e",
    "created_at": "2020-01-23T00:52:07.049138Z",
    "updated_at": "2020-01-23T00:57:27.063889Z",
    "name": "dev",
    "assets": [
        {
            "id": "03fb07bb-5db1-4077-8dea-5d711b272625",
            "class": "us_equity",
            "exchange": "NASDAQ",
            "symbol": "AMD",
            "name": "",
            "status": "active",
            "tradable": true,
            "marginable": true,
            "shortable": true,
            "easy_to_borrow": true
        },
        {
            "id": "4ce9353c-66d1-46c2-898f-fce867ab0247",
            "class": "us_equity",
            "exchange": "NASDAQ",
            "symbol": "NVDA",
            "name": "",
            "status": "active",
            "tradable": true,
            "marginable": true,
            "shortable": true,
            "easy_to_borrow": true
        },
        {
            "id": "bb2a26c0-4c77-4801-8afc-82e8142ac7b8",
            "class": "us_equity",
            "exchange": "NASDAQ",
            "symbol": "NFLX",
            "name": "",
            "status": "active",
            "tradable": true,
            "marginable": true,
            "shortable": true,
            "easy_to_borrow": true
        },
        {
            "id": "24cbba8c-831b-44e2-8503-dd0c2ed7af8f",
            "class": "us_equity",
            "exchange": "NASDAQ",
            "symbol": "PYPL",
            "name": "",
            "status": "active",
            "tradable": true,
            "marginable": true,
            "shortable": true,
            "easy_to_borrow": true
        }
    ]
    }''')
    api.delete_from_watchlist(watchlist_id, symbol)

    # delete a watchlist
    reqmock.delete(
        'https://api.alpaca.markets/v1/watchlists/{}'.format(watchlist_id),
        text='',
        status_code=204,
    )
    api.delete_watchlist(watchlist_id)


def test_errors(reqmock):
    api = tradeapi.REST('key-id', 'secret-key', api_version='v1')

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


def test_no_resource_warning_with_context_manager():
    with pytest.warns(None) as record:  # ensure no warnings are raised
        with tradeapi.REST('key-id', 'secret-key', api_version='v1') as api:
            assert api
    assert not record
