import requests


class REST(object):

    def __init__(self, api_key):
        self._api_key = api_key
        self._session = requests.Session()
        self._base_url = "https://api.stocktwits.com/api/2"

    def _request(self, method, url, params=None):
        params = params or {}
        params["api_key"] = self._api_key
        resp = self._session.request(method, url, params=params)
        resp.raise_for_status()
        return resp.json()

    def get(self, url, params=None):
        return self._request("GET", url, params=params)

    def search_symbol(self, id, callback=None):
        """This allows an API application to search for a symbol directly.

        30 Results will return only ticker symbols.

        :param id:The symbol that you want to search for (Required)
        :param callback: Define your own callback function name, add this parameter as the value
        """
        params = {}

        if callback is not None:
            params["callback"] = callback

        url = "{}/search/symbols.json?q={}".format(self._base_url, id)
        return self.get(url, params)

    def streams_symbol(self, id, since=None, max=None, limit=None, callback=None, filter=None):
        """Returns the most recent 30 messages for the specified symbol.

        Includes symbol object in response.

        :param id: Ticker symbol, Stock ID, or RIC code of the symbol (Required)
        :param since: Returns results with an ID greater than (more recent than) the specified ID
        :param max: Returns results with an ID less than (older than) or equal to the specified ID
        :param limit: Default and max limit is 30. This limit must be a number under 30
        :param callback: Define your own callback function name, add this parameter as the value
        :param filter: Filter messages by links, charts, videos, or top. (Optional)
        """
        params = {}

        if since is not None:
            params["since"] = since
        if max is not None:
            params["max"] = max
        if limit is not None:
            params["limit"] = limit
        if callback is not None:
            params["callback"] = callback
        if filter is not None:
            params["filter"] = filter
        url = "{}/streams/symbol/{}.json".format(self._base_url, id)
        return self.get(url, params)

    def streams_charts(self, since=None, max=None, limit=None, callback=None):
        """Returns the most recent 30 messages that include charts.

        Charts can come in two forms either image file or video file.

        :param since: Returns results with an ID greater than (more recent than) the specified ID
        :param max: Returns results with an ID less than (older than) or equal to the specified ID
        :param limit: Default and max limit is 30. This limit must be a number under 30
        :param callback: Define your own callback function name, add this parameter as the value
        """
        params = {}

        if since is not None:
            params["since"] = since
        if max is not None:
            params["max"] = max
        if limit is not None:
            params["limit"] = limit
        if callback is not None:
            params["callback"] = callback
        url = "{}/streams/charts.json".format(self._base_url)
        return self.get(url, params)

    def streams_trending(self, since=None, max=None, limit=None, callback=None, filter=None):
        """Returns the most recent 30 messages with trending symbols in the last 5 minutes.

        :param since: Returns results with an ID greater than (more recent than) the specified ID
        :param max: Returns results with an ID less than (older than) or equal to the specified ID
        :param limit: Default and max limit is 30. This limit must be a number under 30
        :param callback: Define your own callback function name, add this parameter as the value
        """
        params = {}

        if since is not None:
            params["since"] = since
        if max is not None:
            params["max"] = max
        if limit is not None:
            params["limit"] = limit
        if callback is not None:
            params["callback"] = callback
        if filter is not None:
            params["filter"] = filter
        url = "{}/streams/trending.json".format(self._base_url)
        return self.get(url, params)

    def trending_equities(self, limit=30, callback=None):
        """Returns a list of all the trending equity symbols at the moment requested.

        Trending equities have to have a price over $5. These are updated in 5 minute intervals.
        """
        url = "{}/trending/symbols/equities.json".format(self._base_url)
        return self.get(url, params={"limit": limit, "callback": callback})
