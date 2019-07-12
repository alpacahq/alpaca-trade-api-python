import alpaca_trade_api as tradeapi
import threading
import time
import datetime
import queue

API_KEY = "PKVHWZNVDG78S4QJPWOP"
API_SECRET = "7cvHL2oqFnyKl9qXOaHpDeNhRyG2d93jrDdKjood"
APCA_API_BASE_URL = "https://paper-api.alpaca.markets"

class LongShort:
  def __init__(self):
    self.alpaca = tradeapi.REST(API_KEY,API_SECRET,APCA_API_BASE_URL,'v2')

    stockUniverse = ['DOMO','TLRY','SQ','MRO','AAPL','GM','SNAP','SHOP','SPLK','BA','AMZN','SUI','SUN','TSLA','CGC','SPWR','NIO','CAT','MSFT','PANW','OKTA','TWTR','TM','RTN','ATVI','GS','BAC','MS','TWLO','QCOM',]
    # Format the allStocks variable for use in the class.
    self.allStocks = []
    for stock in stockUniverse:
      self.allStocks.append([stock,0])

    self.long = []
    self.short = []
    self.qShort = None
    self.qLong = None
    self.adjustedQLong = None
    self.adjustedQShort = None
    self.blacklist = set()
    self.longAmount = 0
    self.shortAmount = 0
    self.timeToClose = None
  
  def run(self):
    # First, cancel any existing orders so they don't impact our buying power.
    orders = self.alpaca.list_orders(status="open")
    for order in orders:
      self.alpaca.cancel_order(order.id)
    
    # Wait for market to open.
    print("Waiting for market to open...")
    tAMO = threading.Thread(target=self.awaitMarketOpen)
    tAMO.start()
    tAMO.join()
    print("Market opened.")

    # Rebalance the portfolio every minute, making necessary trades.
    while True:
      tRebalance = threading.Thread(target=self.rebalance)
      tRebalance.start()
      tRebalance.join()

      # Figure out when the market will close so we can prepare to sell beforehand.
      clock = self.alpaca.get_clock()
      closingTime = clock.next_close.replace(tzinfo=datetime.timezone.utc).timestamp()
      currTime = clock.timestamp.replace(tzinfo=datetime.timezone.utc).timestamp()
      self.timeToClose = closingTime - currTime
      
      if(self.timeToClose < (60 * 15)):
        # Close all positions when 15 minutes til market close.
        print("Market closing soon.  Closing positions.")

        positions = self.alpaca.list_positions()
        for position in positions:
          if(position.side == 'long'):
            orderSide = 'sell'
          else:
            orderSide = 'buy'
          qty = abs(position.qty)
          respSO = []
          tSubmitOrder = threading.Thread(target=self.submitOrder(qty,position.symbol,orderSide,respSO))
          tSubmitOrder.start()
          tSubmitOrder.join()
        
          # Run script again after market close for next trading day.
          print("Sleeping until market close (15 minutes).")
          time.sleep(60)
      else:
        time.sleep(60)



  # Wait for market to open.
  def awaitMarketOpen(self):
    isOpen = True#self.alpaca.get_clock().is_open
    while(not isOpen):
      print("spinning")
      time.sleep(2)
      isOpen = self.alpaca.get_clock().is_open
  
  def rebalance(self):
    tRerank = threading.Thread(target=self.rerank)
    tRerank.start()
    tRerank.join()

    # Clear existing orders again.
    orders = self.alpaca.list_orders(status="open")
    for order in orders:
      self.alpaca.cancel_order(order.id)

    # Remove positions that are no longer in the short or long list, and make a list of positions that do not need to change.  Adjust position quantities if needed.
    executed = [[],[]]
    positions = self.alpaca.list_positions()
    for position in positions:
      qty = position.qty
      side = "buy"
      if(self.long.count(position.symbol) == 0):
        # Position is not in long list.
        if(self.short.count(position.symbol) == 0):
          # Position not in short list either.  Clear position.
          if(position.side == "long"):
            side = "sell"
          else:
            side = "buy"
          self.blacklist.remove(position.symbol)
          continue
        else:
          if(position.side == "long"):
            # Position changed from long to short.  Clear long position to prep for short sell.
            qty = qty + self.qShort
          else:
            if(abs(position.qty) == self.qShort):
              # Position is where we want it.  Pass for now.
              executed[1].append(position.symbol)
              self.blacklist.add(position.symbol)
              continue
            else:
              # Need to adjust position amount
              diff = abs(position.qty) - self.qShort
              if(diff > 0):
                # Too many short positions.  Buy some back to rebalance.
                qty = diff
                side = "buy"
              else:
                # Too little short positions.  Sell some more.
                qty = abs(diff)
                side = "sell"
      else:
        if(position.side == "short"):
          # Position changed from short to long.  Clear short position and long instead.
          qty = qty + self.qLong
        else:
          if(position.qty == self.qLong):
            # Position is where we want it.  Pass for now.
            executed[0].append(position.symbol)       
            self.blacklist.add(position.symbol)
            continue
          else:
            # Need to adjust position amount.
            diff = position.qty - self.qLong
            if(diff > 0):
              # Too many long positions.  Sell some to rebalance.
              side = "sell"
            else:
              # Too little long positions.  Buy some more.
              side = "buy"
      tSubmitOrder = threading.Thread(target=self.submitOrder,args=[qty,position.symbol,side])
      tSubmitOrder.start()
      tSubmitOrder.join()
      if(side == "buy"):
        executed[0].append(position.symbol)       
      else:
        executed[1].append(position.symbol)
    
    print("Out of adjustments")

    # Send orders to all remaining stocks in the long and short list.
    respSendBOLong = []
    tSendBOLong = threading.Thread(target=self.sendBatchOrder,args=[self.qLong,self.long,"buy",respSendBOLong])
    tSendBOLong.start()
    tSendBOLong.join()
    respSendBOLong[0][0] += executed[0]
    if(len(respSendBOLong[0][1]) > 0):
      # Handle rejected/incomplete orders and determine new quantities to purchase.
      respGetTPLong = []
      tGetTPLong = threading.Thread(target=self.getTotalPrice,args=[respSendBOLong[0][0],respGetTPLong])
      tGetTPLong.start()
      tGetTPLong.join()
      if (respGetTPLong[0] > 0):
        self.adjustedQLong = self.longAmount // respGetTPLong[0]
      else:
        self.adjustedQLong = -1
    else:
      self.adjustedQLong = -1

    respSendBOShort = []
    tSendBOShort = threading.Thread(target=self.sendBatchOrder,args=[self.qShort,self.short,"sell",respSendBOShort])
    tSendBOShort.start()
    tSendBOShort.join()
    respSendBOShort[0][0] += executed[1]
    if(len(respSendBOShort[0][1]) > 0):
      # Handle rejected/incomplete orders and determine new quantities to purchase.
      respGetTPShort = []
      tGetTPShort = threading.Thread(target=self.getTotalPrice,args=[respSendBOShort[0][0],respGetTPShort])
      tGetTPShort.start()
      tGetTPShort.join()
      if(respGetTPShort[0] > 0):
        self.adjustedQShort = self.shortAmount // respGetTPShort[0]
      else:
        self.adjustedQShort = -1
    else:
      self.adjustedQShort = -1
    
    print("Out of first orders")

    
    # Reorder stocks that didn't throw an error so that the equity quota is reached.
    if(self.adjustedQLong > -1):
      self.qLong = int(self.adjustedQLong - self.qLong)
      respResendBOLong = []
      tResendBOLong = threading.Thread(target=self.sendBatchOrder,args=[self.qLong,respSendBOLong[0][0],"buy",respResendBOLong])
      tResendBOLong.start()
      tResendBOLong.join()

    if(self.adjustedQShort > -1):
      self.qShort = int(self.adjustedQShort - self.qShort)
      respResendBOShort = []
      tResendBOShort = threading.Thread(target=self.sendBatchOrder,args=[self.qShort,respSendBOShort[0][0],"sell",respResendBOShort])
      tResendBOShort.start()
      tResendBOShort.join()
    
    print("Out of reorders")

  # Re-rank all stocks to adjust longs and shorts.
  def rerank(self):
    tRank = threading.Thread(target=self.rank)
    tRank.start()
    tRank.join()

    print("Out of rank")

    # Grabs the top and bottom quarter of the sorted stock list to get the long and short lists.
    longShortAmount = len(self.allStocks) // 4
    self.long = []
    self.short = []
    for i,stockField in enumerate(self.allStocks):
      if(i < longShortAmount):
        self.short.append(stockField[0])
      elif(i > (len(self.allStocks) - 1 - longShortAmount)):
        self.long.append(stockField[0])
      else:
        continue
    
    # Determine amount to long/short based on total stock price of each bucket.
    equity = int(self.alpaca.get_account().equity)

    self.shortAmount = equity * 0.30
    self.longAmount = equity + self.shortAmount

    respGetTPLong = []
    tGetTPLong = threading.Thread(target=self.getTotalPrice,args=[self.long,respGetTPLong])
    tGetTPLong.start()
    tGetTPLong.join()

    respGetTPShort = []
    tGetTPShort = threading.Thread(target=self.getTotalPrice,args=[self.short,respGetTPShort])
    tGetTPShort.start()
    tGetTPShort.join()

    self.qLong = int(self.longAmount // respGetTPLong[0])
    self.qShort = int(self.shortAmount // respGetTPShort[0])

  # Get the total price of the array of input stocks.
  def getTotalPrice(self,stocks,resp):
    totalPrice = 0
    for stock in stocks:
      bars = self.alpaca.get_barset(stock,"minute",1)
      totalPrice += bars[stock][0].c
    resp.append(totalPrice)

  # Submit a batch order that returns completed and uncompleted orders.
  def sendBatchOrder(self,qty,stocks,side,resp):
    executed = []
    incomplete = []
    for stock in stocks:
      if(self.blacklist.isdisjoint(set(stock))):
        respSO = []
        tSubmitOrder = threading.Thread(target=self.submitOrder,args=[qty,stock,side,respSO])
        tSubmitOrder.start()
        tSubmitOrder.join()
        if(respSO[0] == False):
          # Stock order did not go through, add it to incomplete.
          incomplete.append(stock)
        else:
          executed.append(stock)
        respSO.clear()
    resp.append([executed,incomplete])

  # Submit an order if quantity is above 0.
  def submitOrder(self,qty,stock,side,resp):
    if(qty > 0):
      try:
        self.alpaca.submit_order(stock,qty,side,"market","day")
        print("Market order of " + '|' + str(qty) + " " + stock + " " + side + '|' + " completed.")
        resp.append(True)
      except:
        print("Order of " + '|' + str(qty) + " " + stock + " " + side + '|' + " did not go through.")
        resp.append(False)
    else:
      print("Quantity is 0, order of " + '|' + str(qty) + " " + stock + " " + side + '|' + " not completed.")
      resp.append(True)

  # Get percent changes of the stock prices over the past 10 days.
  def getPercentChanges(self):
    length = 10
    startTime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(datetime.datetime.now().replace(tzinfo=datetime.timezone.utc).timestamp() - (60*length)))
    endTime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(datetime.datetime.now().replace(tzinfo=datetime.timezone.utc).timestamp()))
    
    for stock in self.allStocks:
      bars = self.alpaca.get_barset(stock[0],'minute',start=startTime,end=endTime)
      stock[1] = bars[stock[0]][len(bars)-1].c - bars[stock[0]][0].c

  # Mechanism used to rank the stocks, the basis of the Long-Short Equity Strategy.
  def rank(self):
    # Ranks all stocks by percent change over the past 10 days (higher is better).
    tGetPC = threading.Thread(target=self.getPercentChanges)
    tGetPC.start()
    tGetPC.join()

    # Sort the stocks in place by the percent change field (marked by pc).
    self.allStocks.sort(key=lambda x: x[1])


ls = LongShort()
ls.run()