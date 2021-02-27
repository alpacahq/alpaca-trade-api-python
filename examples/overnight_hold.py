import alpaca_trade_api as tradeapi
from alpaca_trade_api.rest import TimeFrame
import pandas as pd
import statistics
import sys
import time

from datetime import datetime, timedelta
from pytz import timezone

stocks_to_hold = 150 # Max 200

# Only stocks with prices in this range will be considered.
max_stock_price = 26
min_stock_price = 6

# API datetimes will match this format. (-04:00 represents the market's TZ.)
api_time_format = '%Y-%m-%dT%H:%M:%S.%f-04:00'

# Rate stocks based on the volume's deviation from the previous 5 days and
# momentum. Returns a dataframe mapping stock symbols to ratings and prices.
# Note: If algo_time is None, the API's default behavior of the current time
# as `end` will be used. We use this for live trading.
def get_ratings(symbols, algo_time):
    assets = api.list_assets()
    assets = [asset for asset in assets if asset.tradable ]
    ratings = pd.DataFrame(columns=['symbol', 'rating', 'price'])
    index = 0
    batch_size = 200 # The maximum number of stocks to request data for
    window_size = 5 # The number of days of data to consider
    formatted_time = None
    if algo_time is not None:
        # Convert the time to something compatable with the Alpaca API.
        formatted_time = algo_time.date().strftime(api_time_format)
    while index < len(assets):
        symbol_batch = [
            asset.symbol for asset in assets[index:index+batch_size]
        ]
        # Retrieve data for this batch of symbols.
        barset = {}
        for symbol in symbol_batch:
            bars = api.get_bars(symbol,
                                TimeFrame.Day,
                                formatted_time - timedelta(days=window_size),
                                formatted_time,
                                limit=window_size,
                                adjustment='raw')
            barset[symbol] = bars

        for symbol in symbol_batch:
            bars = barset[symbol]
            if len(bars) == window_size:
                # Make sure we aren't missing the most recent data.
                latest_bar = bars[-1].t.to_pydatetime().astimezone(
                    timezone('EST')
                )
                gap_from_present = algo_time - latest_bar
                if gap_from_present.days > 1:
                    continue

                # Now, if the stock is within our target range, rate it.
                price = bars[-1].c
                if price <= max_stock_price and price >= min_stock_price:
                    price_change = price - bars[0].c
                    # Calculate standard deviation of previous volumes
                    past_volumes = [bar.v for bar in bars[:-1]]
                    volume_stdev = statistics.stdev(past_volumes)
                    if volume_stdev == 0:
                        # The data for the stock might be low quality.
                        continue
                    # Then, compare it to the change in volume since yesterday.
                    volume_change = bars[-1].v - bars[-2].v
                    volume_factor = volume_change / volume_stdev
                    # Rating = Number of volume standard deviations * momentum.
                    rating = price_change/bars[0].c * volume_factor
                    if rating > 0:
                        ratings = ratings.append({
                            'symbol': symbol,
                            'rating': price_change/bars[0].c * volume_factor,
                            'price': price
                        }, ignore_index=True)
        index += 200
    ratings = ratings.sort_values('rating', ascending=False)
    ratings = ratings.reset_index(drop=True)
    return ratings[:stocks_to_hold]


def get_shares_to_buy(ratings_df, portfolio):
    total_rating = ratings_df['rating'].sum()
    shares = {}
    for _, row in ratings_df.iterrows():
        shares[row['symbol']] = int(
            row['rating'] / total_rating * portfolio / row['price']
        )
    return shares


# Returns a string version of a timestamp compatible with the Alpaca API.
def api_format(dt):
    return dt.strftime(api_time_format)

def backtest(api, days_to_test, portfolio_amount):
    # This is the collection of stocks that will be used for backtesting.
    assets = api.list_assets()
    # Note: for longer testing windows, this should be replaced with a list
    # of symbols that were active during the time period you are testing.
    symbols = [asset.symbol for asset in assets]

    now = datetime.now(timezone('EST'))
    beginning = now - timedelta(days=days_to_test)

    # The calendars API will let us skip over market holidays and handle early
    # market closures during our backtesting window.
    calendars = api.get_calendar(
        start=beginning.strftime("%Y-%m-%d"),
        end=now.strftime("%Y-%m-%d")
    )
    shares = {}
    cal_index = 0
    for calendar in calendars:
        # See how much we got back by holding the last day's picks overnight
        portfolio_amount += get_value_of_assets(api, shares, calendar.date)
        print('Portfolio value on {}: ${:0.2f}'.format(calendar.date.strftime(
            '%Y-%m-%d'), portfolio_amount)
        )

        if cal_index == len(calendars) - 1:
            # We've reached the end of the backtesting window.
            break

        # Get the ratings for a particular day
        ratings = get_ratings(symbols, timezone('EST').localize(calendar.date))
        shares = get_shares_to_buy(ratings, portfolio_amount)
        for _, row in ratings.iterrows():
            # "Buy" our shares on that day and subtract the cost.
            shares_to_buy = shares[row['symbol']]
            cost = row['price'] * shares_to_buy
            portfolio_amount -= cost
        cal_index += 1

    # Print market (S&P500) return for the time period
    sp500_bars = self.oapi.get_bars('SPY',
                                    TimeFrame.Day,
                                    api_format(calendars[0].date),
                                    api_format(calendars[-1].date),
                                    adjustment='raw')
    sp500_change = (sp500_bars[-1].c - sp500_bars[0].c) / sp500_bars[0].c
    print('S&P 500 change during backtesting window: {:.4f}%'.format(
        sp500_change*100)
    )

    return portfolio_amount


# Used while backtesting to find out how much our portfolio would have been
# worth the day after we bought it.
def get_value_of_assets(api, shares_bought, on_date):
    if len(shares_bought.keys()) == 0:
        return 0

    total_value = 0
    formatted_date = api_format(on_date)

    barset = {}
    for symbol in shares_bought.keys():
        bars = api.get_bars(symbol,
                            TimeFrame.Day,
                            on_date,
                            on_date,
                            limit=1,
                            adjustment='raw')
        barset[symbol] = bars
    for symbol in shares_bought:
        total_value += shares_bought[symbol] * barset[symbol][0].o
    return total_value


def run_live(api):
    cycle = 0 # Only used to print a "waiting" message every few minutes.

    # See if we've already bought or sold positions today. If so, we don't want to do it again.
    # Useful in case the script is restarted during market hours.
    bought_today = False
    sold_today = False
    try:
        # The max stocks_to_hold is 200, so we shouldn't see more than 400
        # orders on a given day.
        orders = api.list_orders(
            after=api_format(datetime.today() - timedelta(days=1)),
            limit=400,
            status='all'
        )
        for order in orders:
            if order.side == 'buy':
                bought_today = True
                # This handles an edge case where the script is restarted
                # right before the market closes.
                sold_today = True
                break
            else:
                sold_today = True
    except:
        # We don't have any orders, so we've obviously not done anything today.
        pass

    while True:
        # We'll wait until the market's open to do anything.
        clock = api.get_clock()
        if clock.is_open and not bought_today:
            if sold_today:
                # Wait to buy
                time_until_close = clock.next_close - clock.timestamp
                # We'll buy our shares a couple minutes before market close.
                if time_until_close.seconds <= 120:
                    print('Buying positions...')
                    portfolio_cash = float(api.get_account().cash)
                    ratings = get_ratings(
                        api, None
                    )
                    shares_to_buy = get_shares_to_buy(ratings, portfolio_cash)
                    for symbol in shares_to_buy:
                        api.submit_order(
                            symbol=symbol,
                            qty=shares_to_buy[symbol],
                            side='buy',
                            type='market',
                            time_in_force='day'
                        )
                    print('Positions bought.')
                    bought_today = True
            else:
                # We need to sell our old positions before buying new ones.
                time_after_open = clock.next_open - clock.timestamp
                # We'll sell our shares just a minute after the market opens.
                if time_after_open.seconds >= 60:
                    print('Liquidating positions.')
                    api.close_all_positions()
                sold_today = True
        else:
            bought_today = False
            sold_today = False
            if cycle % 10 == 0:
                print("Waiting for next market day...")
        time.sleep(30)
        cycle+=1



if __name__ == '__main__':
    api = tradeapi.REST()

    if len(sys.argv) < 2:
        print('Error: please specify a command; either "run" or "backtest <cash balance> <number of days to test>".')
    else:
        if sys.argv[1] == 'backtest':
            # Run a backtesting session using the provided parameters
            start_value = float(sys.argv[2])
            testing_days = int(sys.argv[3])
            portfolio_value = backtest(api, testing_days, start_value)
            portfolio_change = (portfolio_value - start_value) / start_value
            print('Portfolio change: {:.4f}%'.format(portfolio_change*100))
        elif sys.argv[1] == 'run':
            run_live(api)
        else:
            print('Error: Unrecognized command ' + sys.argv[1])