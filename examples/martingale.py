import alpaca_trade_api as tradeapi
from alpaca_trade_api.stream import Stream
import datetime

ALPACA_API_KEY = "REPLACE_ME"
ALPACA_SECRET_KEY = "REPLACE_ME"


# Utility to truncate a float value to a certain number of decimal places.
# We'll use this to see if a "penny level" was crossed when we compare prices.
# This is necessary because a price can change by 1/100th of a penny, but we
# can only trade at full-penny increments.
def truncate(val, decimal_places):
    return int(val * 10**decimal_places) / 10**decimal_places


# The MartingaleTrader bets that streaks of increases or decreases in a stock's
# price are likely to break, and increases its bet each time it is wrong.
class MartingaleTrader(object):
    def __init__(self):
        # API authentication keys can be taken from the Alpaca dashboard.
        # https://app.alpaca.markets/paper/dashboard/overview
        self.key_id = ALPACA_API_KEY
        self.secret_key = ALPACA_SECRET_KEY
        self.base_url = 'https://paper-api.alpaca.markets'
        self.data_url = 'https://data.alpaca.markets'

        # The symbol we will be trading
        self.symbol = 'SPY'

        # How many seconds we will wait in between updating the streak values
        self.tick_size = 5
        self.tick_index = 0

        # The percentage of our buying power that we will allocate to a new
        # position after a streak reset
        self.base_bet = 10

        # These variables track the information about the current streak
        self.streak_count = 0
        self.streak_start = 0
        self.streak_increasing = True

        # When this variable is not None, we have an order open
        self.current_order = None

        # The closing price of the last aggregate we saw
        self.last_price = 0

        # used to use tick data as second aggs data (mot every tick, but sec)
        self.last_trade_time = datetime.datetime.utcnow()

        # The connection to the Alpaca API
        self.api = tradeapi.REST(
            self.key_id,
            self.secret_key,
            self.base_url
        )

        # Cancel any open orders so they don't interfere with this script
        self.api.cancel_all_orders()

        try:
            self.position = int(self.api.get_position(self.symbol).qty)
        except:
            # No position exists
            self.position = 0

        # Figure out how much money we have to work with, accounting for margin
        account_info = self.api.get_account()
        self.equity = float(account_info.equity)
        self.margin_multiplier = float(account_info.multiplier)
        total_buying_power = self.margin_multiplier * self.equity
        print(f'Initial total buying power = {total_buying_power}')


    def start_trading(self):
        conn = Stream(
            self.key_id,
            self.secret_key,
            base_url=self.base_url,
            data_feed='iex')  # <- replace to SIP if you have PRO subscription

        # Listen for second aggregates and perform trading logic
        async def handle_bar(bar):
            self.tick_index = (self.tick_index + 1) % self.tick_size
            if self.tick_index == 0:
                # It's time to update

                # Update price info
                tick_open = self.last_price
                tick_close = bar.close
                self.last_price = tick_close

                self.process_current_tick(tick_open, tick_close)

        stream.subscribe_bars(handle_bar, self.symbol)

        # Listen for quote data and perform trading logic
        async def handle_trades(trade):
            now = datetime.datetime.utcnow()
            if now - self.last_trade_time < datetime.timedelta(seconds=1):
                # don't react every tick unless at least 1 second past
                return
            self.last_trade_time = now
            self.tick_index = (self.tick_index + 1) % self.tick_size
            if self.tick_index == 0:
                # It's time to update

                # Update price info
                tick_open = self.last_price
                tick_close = trade.price
                self.last_price = tick_close

                self.process_current_tick(tick_open, tick_close)

        stream.subscribe_trades(handle_trades, self.symbol)

        # Listen for updates to our orders
        async def handle_trade_updates(data):
            symbol = data.order['symbol']
            if symbol != self.symbol:
                # The order was for a position unrelated to this script
                return

            event_type = data.event
            qty = int(data.order['filled_qty'])
            side = data.order['side']
            oid = data.order['id']

            if event_type == 'fill' or event_type == 'partial_fill':
                # Our position size has changed
                self.position = int(data.position_qty)
                print(f'New position size due to order fill: {self.position}')
                if (event_type == 'fill' and self.current_order
                    and self.current_order.id == oid):
                    self.current_order = None
            elif event_type == 'rejected' or event_type == 'canceled':
                if self.current_order and self.current_order.id == oid:
                    # Our last order should be removed
                    self.current_order = None
            elif event_type != 'new':
                print(f'Unexpected order event type {event_type} received')

        stream.subscribe_trade_updates(handle_trade_updates)

        stream.run()

    def process_current_tick(self, tick_open, tick_close):
        # Update streak info
        diff = truncate(tick_close, 2) - truncate(tick_open, 2)
        if diff != 0:
            # There was a meaningful change in the price
            self.streak_count += 1
            increasing = tick_open > tick_close
            if self.streak_increasing != increasing:
                # It moved in the opposite direction of the streak.
                # Therefore, the streak is over, and we should reset.

                # Empty out the position
                self.send_order(0)

                # Reset variables
                self.streak_increasing = increasing
                self.streak_start = tick_open
                self.streak_count = 0
            else:
                # Calculate the number of shares we want to be holding
                total_buying_power = self.equity * \
                                     self.margin_multiplier
                target_value = (2 ** self.streak_count) * \
                               (self.base_bet / 100) * total_buying_power
                if target_value > total_buying_power:
                    # Limit the amount we can buy to a bit (1 share)
                    # less than our total buying power
                    target_value = total_buying_power - self.last_price
                target_qty = int(target_value / self.last_price)
                if self.streak_increasing:
                    target_qty = target_qty * -1
                self.send_order(target_qty)
        # Update our account balance
        self.equity = float(self.api.get_account().equity)

    def send_order(self, target_qty):
        # We don't want to have two orders open at once
        if self.current_order is not None:
            self.api.cancel_order(self.current_order.id)

        delta = target_qty - self.position
        if delta == 0:
            return
        print(f'Ordering towards {target_qty}...')
        try:
            if delta > 0:
                buy_qty = delta
                if self.position < 0:
                    buy_qty = min(abs(self.position), buy_qty)
                print(f'Buying {buy_qty} shares.')
                self.current_order = self.api.submit_order(
                    self.symbol, buy_qty, 'buy',
                    'limit', 'day', self.last_price
                )
            elif delta < 0:
                sell_qty = abs(delta)
                if self.position > 0:
                    sell_qty = min(abs(self.position), sell_qty)
                print(f'Selling {sell_qty} shares.')
                self.current_order = self.api.submit_order(
                    self.symbol, sell_qty, 'sell',
                    'limit', 'day', self.last_price
                )
        except Exception as e:
            print(e)


if __name__ == '__main__':
    trader = MartingaleTrader()
    trader.start_trading()