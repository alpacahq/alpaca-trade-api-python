# flake8: noqa
import requests_mock
import requests
from os import path
import sys
import unittest
from pandas import DataFrame as df, Timestamp
from alpaca_trade_api.alpha_vantage import REST
import pytest
import os


cli = REST("ALPHAVANTAGE_API_KEY")


# def endpoint(params=''):
#     return 'https://www.alphavantage.co/query?{}&apikey=key-id'.format(params)


# def test_get_alpha_vantage():
#     # Sample response
#     # {
#     #     "Global Quote": {
#     #         "01. symbol": "TSLA",
#     #         "02. open": "####",
#     #         "03. high": "####",
#     #         "04. low": "####",
#     #         "05. price": "####",
#     #         "06. volume": "####",
#     #         "07. latest trading day": "yyyy-mm-dd",
#     #         "08. previous close": "####",
#     #         "09. change": "####",
#     #         "10. change percent": "####%"
#     #     }
#     # }

#     # Test Get Method
#     tsla_quote = cli.get(params={'function': 'GLOBAL_QUOTE', 'symbol': 'TSLA'})
#     assert tsla_quote['Global Quote']["01. symbol"] == "TSLA"
#     assert '05. price' in str(tsla_quote['Global Quote'].keys())
#     with pytest.raises(AttributeError):
#         tsla_quote.foo


# def test_historical_quotes():
#     # Sample Response
#     # {
#     # "Meta Data": {
#     #     "1. Information": "Daily Prices (open, high, low, close) and Volumes",
#     #     "2. Symbol": "TSLA",
#     #     "3. Last Refreshed": "yyyy-mm-dd",
#     #     "4. Output Size": "Compact",
#     #     "5. Time Zone": "US/Eastern"
#     # },
#     # "Time Series (Daily)": {
#     #     "yyyy-mm-dd": {
#     #         "1. open": "####",
#     #         "2. high": "####",
#     #         "3. low": "####",
#     #         "4. close": "####",
#     #         "5. volume": "####"
#     #     },
#     #     "yyyy-mm-dd": {
#     #         "1. open": "####",
#     #         "2. high": "####",
#     #         "3. low": "####",
#     #         "4. close": "####",
#     #         "5. volume": "####"
#     #     }
#     #   }

#     historic_quotes = cli.historic_quotes(
#         'TSLA', adjusted=False, outputsize='full', cadence='daily', output_format=None)
#     assert len(historic_quotes.keys()) > 0
#     assert len(historic_quotes) > 0
#     with pytest.raises(AttributeError):
#         historic_quotes.foo


# def test_intraday_quotes():
#     # Sample Response
#     # {
#     # "Meta Data": {
#     #     "1. Information": "Intraday (5min) open, high, low, close prices and volume",
#     #     "2. Symbol": "MSFT",
#     #     "3. Last Refreshed": "2020-01-13 16:00:00",
#     #     "4. Interval": "5min",
#     #     "5. Output Size": "Compact",
#     #     "6. Time Zone": "US/Eastern"
#     # },
#     # "Time Series (5min)": {
#     #     "2020-01-13 16:00:00": {
#     #         "1. open": "163.1300",
#     #         "2. high": "163.3200",
#     #         "3. low": "163.1100",
#     #         "4. close": "163.2800",
#     #         "5. volume": "1094345"
#     #     },
#     #     "2020-01-13 15:55:00": {
#     #         "1. open": "162.9200",
#     #         "2. high": "163.1500",
#     #         "3. low": "162.9000",
#     #         "4. close": "163.1351",
#     #         "5. volume": "522600"
#     #     }
#     # }

#     intraday_quotes = cli.intraday_quotes(
#         'TSLA', interval='5min', outputsize='full', output_format=None)
#     assert len(intraday_quotes.keys()) > 0
#     assert len(intraday_quotes) > 0
#     with pytest.raises(AttributeError):
#         intraday_quotes.foo


# def test_current_quote():
#     # Sample response
#     # {
#     #     "Global Quote": {
#     #         "01. symbol": "TSLA",
#     #         "02. open": "####",
#     #         "03. high": "####",
#     #         "04. low": "####",
#     #         "05. price": "####",
#     #         "06. volume": "####",
#     #         "07. latest trading day": "yyyy-mm-dd",
#     #         "08. previous close": "####",
#     #         "09. change": "####",
#     #         "10. change percent": "####%"
#     #     }
#     # }

#     # Test Get Method
#     tsla_quote = cli.current_quote('TSLA')
#     assert tsla_quote["01. symbol"] == "TSLA"
#     assert '05. price' in str(tsla_quote.keys())
#     with pytest.raises(AttributeError):
#         tsla_quote.foo


# def test_search_endpoint():
#     # Sample response
#     # {
#     #     "bestMatches": [
#     #         {
#     #             "1. symbol": "BA",
#     #             "2. name": "The Boeing Company",
#     #             "3. type": "Equity",
#     #             "4. region": "United States",
#     #             "5. marketOpen": "09:30",
#     #             "6. marketClose": "16:00",
#     #             "7. timezone": "UTC-05",
#     #             "8. currency": "USD",
#     #             "9. matchScore": "1.0000"
#     #         },
#     #         {
#     #             "1. symbol": "BABA",
#     #             "2. name": "Alibaba Group Holding Limited",
#     #             "3. type": "Equity",
#     #             "4. region": "United States",
#     #             "5. marketOpen": "09:30",
#     #             "6. marketClose": "16:00",
#     #             "7. timezone": "UTC-05",
#     #             "8. currency": "USD",
#     #             "9. matchScore": "0.8000"
#     #         }
#     # }
#     search_endpoint = cli.search_endpoint(keywords='BA')
#     assert search_endpoint["bestMatches"][0]["2. name"] == "The Boeing Company"
#     assert "4. region" in str(search_endpoint["bestMatches"][0].keys())
#     with pytest.raises(AttributeError):
#         search_endpoint.foo


class TestAlphaVantage(unittest.TestCase):

    _API_KEY_TEST = "test"
    _API_EQ_NAME_TEST = 'MSFT'

    @staticmethod
    def get_file_from_url(url):
        """
            Return the file name used for testing, found in the test data folder
            formed using the original url
        """
        tmp = url
        for ch in [':', '/', '.', '?', '=', '&', ',']:
            if ch in tmp:
                tmp = tmp.replace(ch, '_')
        path_dir = path.join(path.dirname(
            path.abspath(__file__)), 'test_data/')
        return path.join(path.join(path_dir, tmp))

    @requests_mock.Mocker()
    def test_get_method(self, mock_request):
        """ Test that api call returns a json file as requested
        """
        cli = REST(TestAlphaVantage._API_KEY_TEST)
        params = {'function': 'TIME_SERIES_INTRADAY',
                  'symbol': 'MSFT', 'interval': '1min'}
        url = 'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol=MSFT&interval=1min&apikey=test'
        path_file = self.get_file_from_url("mock_time_series")
        with open(path_file) as f:
            mock_request.get(url, text=f.read())
            data = cli.get(params)
            self.assertIsInstance(
                data, dict, 'Result Data must be a dictionary')

    @requests_mock.Mocker()
    def test_historic_quotes(self, mock_request):
        """ Test that api call returns a json file as requested
        """
        cli = REST(TestAlphaVantage._API_KEY_TEST)
        url = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=MSFT&outputsize=full&apikey=test&datatype=json'
        path_file = self.get_file_from_url("mock_time_series_daily")
        with open(path_file) as f:
            mock_request.get(url, text=f.read())
            data = cli.historic_quotes('MSFT', cadence='daily')
            self.assertIsInstance(
                data, dict, 'Result Data must be a dictionary')

    @requests_mock.Mocker()
    def test_intraday_quotes_pandas(self, mock_request):
        """ Test that api call returns a json file as requested
        """
        cli = REST(TestAlphaVantage._API_KEY_TEST)
        url = "https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol=MSFT&interval=1min&outputsize=full&apikey=test&datatype=json"
        path_file = self.get_file_from_url("mock_time_series")
        with open(path_file) as f:
            mock_request.get(url, text=f.read())
            data = cli.intraday_quotes(
                "MSFT", interval='1min', outputsize='full', output_format='pandas')
            self.assertIsInstance(
                data, df, 'Result Data must be a pandas data frame')

    @requests_mock.Mocker()
    def test_current_quote(self, mock_request):
        """ Test that api call returns a json file as requested
        """
        cli = REST(TestAlphaVantage._API_KEY_TEST)
        url = "https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=MSFT&apikey=test&datatype=json"
        path_file = self.get_file_from_url("global_quote")
        with open(path_file) as f:
            mock_request.get(url, text=f.read())
            data = cli.current_quote("MSFT")
            self.assertIsInstance(
                data, dict, 'Result Data must be a dict')

    @requests_mock.Mocker()
    def test_current_quote(self, mock_request):
        """ Test that api call returns a json file as requested
        """
        cli = REST(TestAlphaVantage._API_KEY_TEST)
        url = "https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=MSFT&apikey=test&datatype=json"
        path_file = self.get_file_from_url("global_quote")
        with open(path_file) as f:
            mock_request.get(url, text=f.read())
            data = cli.current_quote("MSFT")
            self.assertIsInstance(
                data, dict, 'Result Data must be a dict')

    @requests_mock.Mocker()
    def test_search_endpoint(self, mock_request):
        """ Test that api call returns a json file as requested
        """
        cli = REST(TestAlphaVantage._API_KEY_TEST)
        url = "https://www.alphavantage.co/query?function=SYMBOL_SEARCH&keywords=BA&datatype=json&apikey=test"
        path_file = self.get_file_from_url("symbol_search")
        with open(path_file) as f:
            mock_request.get(url, text=f.read())
            data = cli.search_endpoint("BA")
            self.assertIsInstance(
                data, dict, 'Result Data must be a dict')

    @requests_mock.Mocker()
    def test_techindicators(self, mock_request):
        """ Test that api call returns a json file as requested
        """
        cli = REST(TestAlphaVantage._API_KEY_TEST)
        url = "https://www.alphavantage.co/query?function=SMA&interval=weekly&time_period=10&apikey=test"
        path_file = self.get_file_from_url("mock_technical_indicator")
        with open(path_file) as f:
            mock_request.get(url, text=f.read())
            data = cli.techindicators(
                techindicator='SMA', interval='weekly', time_period=10)
            self.assertIsInstance(
                data, dict, 'Result Data must be a dict')

    @requests_mock.Mocker()
    def test_sector_pandas(self, mock_request):
        """ Test that api call returns a json file as requested
        """
        cli = REST(TestAlphaVantage._API_KEY_TEST)
        url = "https://www.alphavantage.co/query?function=SECTOR&apikey=test"
        path_file = self.get_file_from_url("mock_sector")
        with open(path_file) as f:
            mock_request.get(url, text=f.read())
            data = cli.sector()
            self.assertIsInstance(
                data, dict, 'Result Data must be a dict')
