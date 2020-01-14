import requests
from alpha_vantage.timeseries import TimeSeries
from alpha_vantage.cryptocurrencies import CryptoCurrencies
from alpha_vantage.foreignexchange import ForeignExchange
from alpha_vantage.sectorperformance import SectorPerformances
from alpha_vantage.techindicators import TechIndicators
from alpaca_trade_api.common import get_alpha_vantage_credentials


class REST(object):

    def __init__(self, api_key):
        self._api_key = get_alpha_vantage_credentials(api_key)
        self._session = requests.Session()
        self._timeseries = TimeSeries(key=self._api_key)
        self._cryptocurrencies = CryptoCurrencies(key=self._api_key)
        self._foreignexchange = ForeignExchange(key=self._api_key)
        self._sectorperformance = SectorPerformances(key=self._api_key)
        self._techindicators = TechIndicators(key=self._api_key)

    def _request(self, method, params=None):
        url = 'https://www.alphavantage.co/query?'
        params = params or {}
        params['apikey'] = self._api_key
        resp = self._session.request(method, url, params=params)
        resp.raise_for_status()
        return resp.json()

    def get(self, params=None):
        ''' Customizable endpoint, where you can pass all 
        keywords/paramters from the documentation:
        https://www.alphavantage.co/documentation/#

        Returns:
            pandas, csv, or json
        '''
        return self._request('GET', params=params)

    def historic_quotes(self, symbol, adjusted=False, outputsize='full', cadence='daily', output_format=None):
        ''' Returns the one of the TIME_SERIES_* endpoints of the Alpha Vantage API.

        Params:
            symbol: The ticker to return
            adjusted: Return the adjusted prices
            cadence: Choose between ['daily', 'weekly', 'monthly'], to return the cadence
            output_format: Choose between['json', 'csv', 'pandas']

        Returns:
            pandas, csv, or json
        '''
        if output_format:
            self._timeseries.output_format = output_format
        if cadence == 'daily':
            data, _ = self._timeseries.get_daily_adjusted(
                symbol=symbol, outputsize=outputsize) if adjusted else self._timeseries.get_daily(symbol=symbol, outputsize=outputsize)
        if cadence == 'weekly':
            data, _ = self._timeseries.get_weekly_adjusted(
                symbol=symbol) if adjusted else self._timeseries.get_weekly(symbol=symbol)
        if cadence == 'monthly':
            data, _ = self._timeseries.get_monthly_adjusted(
                symbol=symbol) if adjusted else self._timeseries.get_monthly(symbol=symbol)
        return data

    def intraday_quotes(self, symbol, interval='5min', outputsize='full', output_format=None):
        ''' Returns the TIME_SERIES_INTRADAY endpoint of the Alpha Vantage API.

        Params:
            symbol: The ticker to return
            interval: Choose between['1min', '5min', '15min', '30min', '60min']
            output_format: Choose between['json', 'csv', 'pandas']

        Returns:
            pandas, csv, or json
        '''
        if output_format:
            self._timeseries.output_format = output_format
        data, _ = self._timeseries.get_intraday(
            symbol=symbol, interval=interval, outputsize=outputsize)
        return data

    def current_quote(self, symbol):
        ''' Returns the GLOBAL_QUOTE endpoint
        of the Alpha Vantage API.

        Params:
            symbol: The ticker to return
            output_format: Choose between['json', 'csv', 'pandas']

        Returns:
            pandas, csv, or json
        '''
        data, _ = self._timeseries.get_quote_endpoint(symbol=symbol)
        return data

    def last_quote(self, symbol):
        return self.current_quote(symbol)

    def company(self, symbol, datatype='json'):
        return self.search_endpoint(symbol, datatype=datatype)

    def search_endpoint(self, keywords, datatype='json'):
        '''Search endpoint returns a list of possible companies
        that correspond to keywords

        Params:
            datatype: csv, json, or pandas
            keywords: ex. keywords=microsoft

        Returns:
            pandas, csv, or json
        '''
        params = {'function': 'SYMBOL_SEARCH',
                  'keywords': keywords, 'datatype': datatype}
        return self.get(params)

    def historic_fx_quotes(self, from_symbol, to_symbol, outputsize='full', cadence='daily', output_format=None):
        ''' Returns the one of the FX_* endpoints of the Alpha Vantage API.

        Params:
            from_currency: The symbol to convert
            to_currency: The symbol to convert to
            cadence: Choose between ['daily', 'weekly', 'monthly'], to return the cadence
            output_format: Choose between['json', 'csv', 'pandas']

        Returns:
            pandas, csv, or json
        '''
        if output_format:
            self._foreignexchange.output_format = output_format
        if cadence == 'daily':
            data, _ = self._foreignexchange.get_currency_exchange_daily(
                from_symbol=from_symbol, to_symbol=to_symbol, outputsize=outputsize)
        if cadence == 'weekly':
            data, _ = self._foreignexchange.get_currency_exchange_weekly(
                from_symbol=from_symbol, to_symbol=to_symbol, outputsize=outputsize)
        if cadence == 'monthly':
            data, _ = self._foreignexchange.get_currency_exchange_monthly(
                from_symbol=from_symbol, to_symbol=to_symbol, utputsize=outputsize)
        return data

    def intraday_fx_quotes(self, from_symbol, to_symbol, interval='5min', outputsize='full', output_format=None):
        ''' Returns the FX_INTRADAY endpoint of the Alpha Vantage API.

        Params:
            from_currency: The symbol to convert
            to_currency: The symbol to convert to
            interval: Choose between['1min', '5min', '15min', '30min', '60min']
            output_format: Choose between['json', 'csv', 'pandas']

        Returns:
            pandas, csv, or json
        '''
        if output_format:
            self._foreignexchange.output_format = output_format
        data, _ = self._foreignexchange.get_currency_exchange_intraday(
            from_symbol=from_symbol, to_symbol=to_symbol, interval=interval, outputsize=outputsize)
        return data

    def exchange_rate(self, from_currency, to_currency):
        ''' Returns the exchange rate of two currencies, digital or physical.
        CURRENCY_EXCHANGE_RATE endpoint of the Alpha Vantage API

        Params:
            from_currency: The symbol to convert
            to_currency: The symbol to convert to

        Returns:
            json
        '''
        params = {'function': "CURRENCY_EXCHANGE_RATE",
                  'from_currency': from_currency, 'to_currency': to_currency}
        data = self.get(params)
        return data

    def historic_cryptocurrency_quotes(self, symbol, market, cadence='daily', output_format=None):
        ''' Returns the one of the DIGITAL_CURRENCY_* endpoints of the Alpha Vantage API.

        Params:
            symbol: The cryptocurrency to return
            market: The market it's being sold on
            cadence: Choose between ['daily', 'weekly', 'monthly'], to return the cadence
            output_format: Choose between['json', 'csv', 'pandas']

        Returns:
            pandas, csv, or json
        '''
        if output_format:
            self._cryptocurrencies.output_format = output_format
        if cadence == 'daily':
            data, _ = self._cryptocurrencies.get_digital_currency_daily(
                symbol=symbol, market=market)
        if cadence == 'weekly':
            data, _ = self._cryptocurrencies.get_digital_currency_weekly(
                symbol=symbol, market=market)
        if cadence == 'monthly':
            data, _ = self._cryptocurrencies.get_digital_currency_monthly(
                symbol=symbol, market=market)
        return data

    def techindicators(self, techindicator='SMA', output_format='json', **kwargs):
        ''' Returns the one of the technical indicator endpoints of the Alpha Vantage API.

        Params:
            techindicator: The technical indicator of choice
            params: Each technical indicator has additional optional parameters

        Returns:
            pandas, csv, or json
        '''
        if output_format:
            self._techindicators.output_format = output_format
        params = {'function': techindicator}
        for key, value in kwargs.items():
            params[key] = value
        data = self.get(params)
        return data

    def sector(self):
        ''' Returns the sector performances

        Returns:
            pandas, csv, or json
        '''
        data, _ = self._sectorperformance.get_sector()
        return data
