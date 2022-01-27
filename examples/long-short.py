import datetime
import time
from typing import List

import alpaca_trade_api as tradeapi
from alpaca_trade_api.common import URL
from alpaca_trade_api.rest import TimeFrame

API_KEY = "YOUR_API_KEY_HERE"
API_SECRET = "YOUR_API_SECRET_HERE"
APCA_API_BASE_URL = "https://paper-api.alpaca.markets"


class LongShort:
    def __init__(self):
        self.alpaca = tradeapi.REST(API_KEY, API_SECRET, URL(APCA_API_BASE_URL), 'v2')

        stock_universe = ['DOMO', 'TLRY', 'SQ', 'MRO', 'AAPL', 'GM', 'SNAP', 'SHOP',
                          'SPLK', 'BA', 'AMZN', 'SUI', 'SUN', 'TSLA', 'CGC', 'SPWR',
                          'NIO', 'CAT', 'MSFT', 'PANW', 'OKTA', 'TWTR', 'TM', 'RTN',
                          'ATVI', 'GS', 'BAC', 'MS', 'TWLO', 'QCOM', ]
        # Format the allStocks variable for use in the class.
        self.all_stocks = []
        for stock in stock_universe:
            self.all_stocks.append([stock, 0])

        self.long = []
        self.short = []
        self.q_short = None
        self.q_long = None
        self.adjusted_q_long = None
        self.adjusted_q_short = None
        self.blacklist = set()
        self.long_amount = 0
        self.short_amount = 0
        self.time_to_close = None

    def run(self):
        # First, cancel any existing orders so they don't impact our buying power.
        orders = self.alpaca.list_orders(status="open")
        for order in orders:
            self.alpaca.cancel_order(order.id)

        # Wait for market to open.
        print("Waiting for market to open...")
        self.await_market_open()
        print("Market opened.")

        # Rebalance the portfolio every minute, making necessary trades.
        while True:

            # Figure out when the market will close so we can prepare to sell beforehand.
            clock = self.alpaca.get_clock()
            closing_time = clock.next_close.replace(tzinfo=datetime.timezone.utc).timestamp()
            curr_time = clock.timestamp.replace(tzinfo=datetime.timezone.utc).timestamp()
            self.time_to_close = closing_time - curr_time

            if self.time_to_close < (60 * 15):
                # Close all positions when 15 minutes til market close.
                print("Market closing soon.  Closing positions.")

                positions = self.alpaca.list_positions()
                for position in positions:
                    if position.side == 'long':
                        order_side = 'sell'
                    else:
                        order_side = 'buy'
                    qty = abs(int(float(position.qty)))
                    self.submit_order(qty, position.symbol, order_side)

                # Run script again after market close for next trading day.
                print("Sleeping until market close (15 minutes).")
                time.sleep(60 * 15)
            else:
                # Rebalance the portfolio.
                self.rebalance()
                time.sleep(60)

    # Wait for market to open.
    def await_market_open(self):
        is_open = self.alpaca.get_clock().is_open
        while not is_open:
            clock = self.alpaca.get_clock()
            opening_time = clock.next_open.replace(tzinfo=datetime.timezone.utc).timestamp()
            curr_time = clock.timestamp.replace(tzinfo=datetime.timezone.utc).timestamp()
            time_to_open = int((opening_time - curr_time) / 60)
            print(str(time_to_open) + " minutes til market open.")
            time.sleep(60)
            is_open = self.alpaca.get_clock().is_open

    def rebalance(self):
        self.rerank()

        # Clear existing orders again.
        orders = self.alpaca.list_orders(status="open")
        for order in orders:
            self.alpaca.cancel_order(order.id)

        print("We are taking a long position in: " + str(self.long))
        print("We are taking a short position in: " + str(self.short))
        # Remove positions that are no longer in the short or long list,
        # and make a list of positions that do not need to change. Adjust position quantities if needed.
        executed = [[], []]
        positions = self.alpaca.list_positions()
        self.blacklist.clear()
        for position in positions:
            if self.long.count(position.symbol) == 0:
                # Position is not in long list.
                if self.short.count(position.symbol) == 0:
                    # Position not in short list either.  Clear position.
                    if position.side == "long":
                        side = "sell"
                    else:
                        side = "buy"
                    self.submit_order(abs(int(float(position.qty))), position.symbol, side)
                else:
                    # Position in short list.
                    if position.side == "long":
                        # Position changed from long to short.  Clear long position to prepare for short position.
                        side = "sell"
                        self.submit_order(int(float(position.qty)), position.symbol, side)
                    else:
                        if abs(int(float(position.qty))) == self.q_short:
                            # Position is where we want it.  Pass for now.
                            pass
                        else:
                            # Need to adjust position amount
                            diff = abs(int(float(position.qty))) - self.q_short
                            if diff > 0:
                                # Too many short positions.  Buy some back to rebalance.
                                side = "buy"
                            else:
                                # Too little short positions.  Sell some more.
                                side = "sell"
                            self.submit_order(abs(diff), position.symbol, side)
                        executed[1].append(position.symbol)
                        self.blacklist.add(position.symbol)
            else:
                # Position in long list.
                if position.side == "short":
                    # Position changed from short to long.  Clear short position to prepare for long position.
                    self.submit_order(abs(int(float(position.qty))), position.symbol, "buy")
                else:
                    if int(float(position.qty)) == self.q_long:
                        # Position is where we want it.  Pass for now.
                        pass
                    else:
                        # Need to adjust position amount.
                        diff = abs(int(float(position.qty))) - self.q_long
                        if diff > 0:
                            # Too many long positions.  Sell some to rebalance.
                            side = "sell"
                        else:
                            # Too little long positions.  Buy some more.
                            side = "buy"
                        self.submit_order(abs(diff), position.symbol, side)
                    executed[0].append(position.symbol)
                    self.blacklist.add(position.symbol)

        # Send orders to all remaining stocks in the long and short list.
        resp_send_bo_long = self.send_batch_order(self.q_long, self.long, "buy")
        resp_send_bo_long[0][0] += executed[0]
        if len(resp_send_bo_long[0][1]) > 0:
            # Handle rejected/incomplete orders and determine new quantities to purchase.
            resp_get_tp_long = self.get_total_price(resp_send_bo_long[0][0])
            if resp_get_tp_long > 0:
                self.adjusted_q_long = self.long_amount // resp_get_tp_long
            else:
                self.adjusted_q_long = -1
        else:
            self.adjusted_q_long = -1

        resp_send_bo_short = self.send_batch_order(self.q_short, self.short, "sell")
        resp_send_bo_short[0][0] += executed[1]
        if len(resp_send_bo_short[0][1]) > 0:
            # Handle rejected/incomplete orders and determine new quantities to purchase.
            resp_get_tp_short = self.get_total_price(resp_send_bo_short[0][0])
            if resp_get_tp_short > 0:
                self.adjusted_q_short = self.short_amount // resp_get_tp_short
            else:
                self.adjusted_q_short = -1
        else:
            self.adjusted_q_short = -1

        # Reorder stocks that didn't throw an error so that the equity quota is reached.
        if self.adjusted_q_long > -1:
            self.q_long = int(self.adjusted_q_long - self.q_long)
            for stock in resp_send_bo_long[0][0]:
                self.submit_order(self.q_long, stock, "buy")

        if self.adjusted_q_short > -1:
            self.q_short = int(self.adjusted_q_short - self.q_short)
            for stock in resp_send_bo_short[0][0]:
                self.submit_order(self.q_short, stock, "sell")

    # Re-rank all stocks to adjust longs and shorts.
    def rerank(self):
        self.rank()

        # Grabs the top and bottom quarter of the sorted stock list to get the long and short lists.
        long_short_amount = len(self.all_stocks) // 4
        self.long = []
        self.short = []
        for i, stock_field in enumerate(self.all_stocks):
            if i < long_short_amount:
                self.short.append(stock_field[0])
            elif i > (len(self.all_stocks) - 1 - long_short_amount):
                self.long.append(stock_field[0])
            else:
                continue

        # Determine amount to long/short based on total stock price of each bucket.
        equity = int(float(self.alpaca.get_account().equity))

        self.short_amount = equity * 0.30
        self.long_amount = equity - self.short_amount

        resp_get_tp_long = self.get_total_price(self.long)

        resp_get_tp_short = self.get_total_price(self.short)

        self.q_long = int(self.long_amount // resp_get_tp_long)
        self.q_short = int(self.short_amount // resp_get_tp_short)

    # Get the total price of the array of input stocks.
    def get_total_price(self, stocks) -> float:
        total_price = 0
        for stock in stocks:
            bars = self.alpaca.get_bars(stock, TimeFrame.Minute,
                                        datetime.date.today().isoformat(),
                                        datetime.date.today().isoformat(), limit=1,
                                        adjustment='raw')

            total_price += bars[stock][0].c
        return total_price

    # Submit a batch order that returns completed and uncompleted orders.
    def send_batch_order(self, qty, stocks, side) -> List[List[str]]:
        executed = []
        incomplete = []
        for stock in stocks:
            if self.blacklist.isdisjoint({stock}):
                success = self.submit_order(qty, stock, side)
                if not success:
                    # Stock order did not go through, add it to incomplete.
                    incomplete.append(stock)
                else:
                    executed.append(stock)
        return [executed, incomplete]

    # Submit an order if quantity is above 0.
    def submit_order(self, qty, stock, side) -> bool:
        if qty > 0:
            try:
                self.alpaca.submit_order(stock, qty, side, "market", "day")
                print(f"Market order of | {qty} {stock} {side} | completed.")
                return True
            except Exception as e:
                print(f"Order of | {qty} {stock} {side} | did not go through. Exception: {e}")
                return False
        else:
            print("Quantity is 0, order of | {qty} {stock} {side} | not completed.")
            return True

    # Get percent changes of the stock prices over the past 10 minutes.
    def get_percent_changes(self) -> None:
        length = 10
        for i, stock in enumerate(self.all_stocks):
            bars = self.alpaca.get_bars(stock[0], TimeFrame.Minute,
                                        datetime.date.today().isoformat(),
                                        datetime.date.today().isoformat(), limit=length,
                                        adjustment='raw')
            self.all_stocks[i][1] = (bars[stock[0]][len(bars[stock[0]]) - 1].c -
                                     bars[stock[0]][0].o) / bars[stock[0]][0].o

    # Mechanism used to rank the stocks, the basis of the Long-Short Equity Strategy.
    def rank(self):
        # Ranks all stocks by percent change over the past 10 minutes (higher is better).
        self.get_percent_changes()

        # Sort the stocks in place by the percent change field (marked by pc).
        self.all_stocks.sort(key=lambda x: x[1])


# Run the LongShort class
ls = LongShort()
ls.run()
