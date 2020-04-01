from alpaca_trade_api.stocktwits import REST
import unittest


class TestStockTwits(unittest.TestCase):

    stocktwits = REST(api_key=None)

    def test_search_symbol(self):

        symbol = self.stocktwits.search_symbol("AAPL")
        self.assertIsInstance(symbol, dict)
        self.assertEqual(symbol["response"]["status"], 200)
        self.assertIsInstance(symbol["results"], list)
        self.assertIn("type", list(symbol["results"][0].keys()))
        self.assertIn("title", list(symbol["results"][0].keys()))
        self.assertIn("symbol", list(symbol["results"][0].keys()))
        self.assertIn("exchange", list(symbol["results"][0].keys()))
        self.assertIn("id", list(symbol["results"][0].keys()))

    def test_streams_symbol(self):

        symbol = self.stocktwits.streams_symbol("AAPL")
        self.assertIsInstance(symbol, dict)
        self.assertEqual(symbol["response"]["status"], 200)
        self.assertIn("id", symbol["symbol"].keys())
        self.assertIn("symbol", symbol["symbol"].keys())
        self.assertIn("title", symbol["symbol"].keys())
        self.assertIn("aliases", symbol["symbol"].keys())
        self.assertIn("is_following", symbol["symbol"].keys())
        self.assertIn("watchlist_count", symbol["symbol"].keys())

    def test_streams_charts(self):

        charts = self.stocktwits.streams_charts()
        self.assertIsInstance(charts, dict)
        self.assertEqual(charts["response"]["status"], 200)
        self.assertIsInstance(charts["messages"], list)
        self.assertIsInstance(charts["cursor"], dict)
        self.assertIn("id", list(charts["messages"][0].keys()))
        self.assertIn("body", list(charts["messages"][0].keys()))
        self.assertIn("created_at", list(charts["messages"][0].keys()))

    def test_streams_trending(self):
        trending = self.stocktwits.streams_trending()
        self.assertIsInstance(trending, dict)
        self.assertEqual(trending["response"]["status"], 200)
        self.assertIsInstance(trending["messages"], list)
        self.assertIsInstance(trending["cursor"], dict)
        self.assertIn("id", list(trending["messages"][0].keys()))
        self.assertIn("body", list(trending["messages"][0].keys()))
        self.assertIn("created_at", list(trending["messages"][0].keys()))
        self.assertIn("user", list(trending["messages"][0].keys()))
        self.assertIn("source", list(trending["messages"][0].keys()))
        self.assertIn("symbols", list(trending["messages"][0].keys()))
        self.assertIn("mentioned_users", list(trending["messages"][0].keys()))
        self.assertIn("entities", list(trending["messages"][0].keys()))
        self.assertIn("filters", list(trending["messages"][0].keys()))
        self.assertIsInstance(trending, dict)

    def test_trending_equities(self):
        trending_equities = self.stocktwits.trending_equities()
        self.assertIsInstance(trending_equities, dict)
        self.assertEqual(trending_equities["response"]["status"], 200)
        self.assertIsInstance(trending_equities["symbols"], list)
        self.assertIn("id", list(trending_equities["symbols"][0].keys()))
        self.assertIn("symbol", list(trending_equities["symbols"][0].keys()))
        self.assertIn("title", list(trending_equities["symbols"][0].keys()))
        self.assertIn("aliases", list(trending_equities["symbols"][0].keys()))
        self.assertIn("is_following", list(trending_equities["symbols"][0].keys()))
        self.assertIn("watchlist_count", list(trending_equities["symbols"][0].keys()))
