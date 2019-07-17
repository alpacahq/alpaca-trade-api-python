# Examples

This directory contains example trading algorithms that connect to the paper-trading API.  These scripts are meant to be run in a Node.js app, where you first install the Alpaca node module, then run the trading algorithm.  Please note you will need to replace the `API_KEY` and `API_SECRET` parameters at the top of the file with your own information from the [Alpaca dashboard](https://app.alpaca.markets/).  Please also note that the performance of these scripts in a real trading environment is not guaranteed. While they are written with the goal of showing realistic uses of the SDK, there is no guarantee that the strategies they outline are a good fit for your own brokerage account.

## Long-Short Equity

This trading algorithm implements the long-short equity strategy.  This means that the algorithm will rank a given universe of stocks based on a certain metric, and long the top ranked stocks and short the lower ranked stocks.  More specifically, the algorithm uses the frequently used 130/30 percent equity split between longs and shorts (130% of equity used for longs, 30% of equity used for shorts).  The algorithm will then grab the top and bottom 25% of stocks, and long or short them accordingly.  The algorithm will purchase equal quantities across a bucket of stocks, so all stocks in the long bucket are ordered with the same quantity (same with the short bucket).  After every minute, the algorithm will re-rank the stocks and make adjustments to the position if necessary.

Some stocks cannot be shorted.  In this case, the algorithm uses the leftover equity from the stocks that could not be shorted and shorts the stocks have already been shorted.

The algorithm uses percent change in stock price over the past 10 minutes to rank the stocks, where the stocks the rose the most are longed and the ones that sunk the most are shorted.