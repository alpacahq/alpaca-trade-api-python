import os
from typing import Tuple
import dateutil.parser

Credentials = Tuple[str, str, str]


class URL(str):
    def __new__(cls, *value):
        """
        note: we use *value and v0 to allow an empty URL string
        """
        if value:
            v0 = value[0]
            if not (isinstance(v0, str) or isinstance(v0, URL)):
                raise TypeError(f'Unexpected type for URL: "{type(v0)}"')
            if not (v0.startswith('http://') or v0.startswith('https://') or
                    v0.startswith('ws://') or v0.startswith('wss://')):
                raise ValueError(f'Passed string value "{v0}" is not an'
                                 f' "http*://" or "ws*://" URL')
        return str.__new__(cls, *value)


class DATE(str):
    """
    date string in the format YYYY-MM-DD
    """
    def __new__(cls, value):
        if not value:
            raise ValueError('Unexpected empty string')
        if not isinstance(value, str):
            raise TypeError(f'Unexpected type for DATE: "{type(value)}"')
        if value.count("-") != 2:
            raise ValueError(f'Unexpected date structure. expected '
                             f'"YYYY-MM-DD" got {value}')
        try:
            dateutil.parser.parse(value)
        except Exception as e:
            msg = f"{value} is not a valid date string: {e}"
            raise Exception(msg)
        return str.__new__(cls, value)


def get_base_url() -> URL:
    return URL(os.environ.get(
        'APCA_API_BASE_URL', 'https://api.alpaca.markets').rstrip('/'))


def get_data_url() -> URL:
    return URL(os.environ.get(
        'APCA_API_DATA_URL', 'https://data.alpaca.markets').rstrip('/'))


def get_credentials(key_id: str = None,
                    secret_key: str = None,
                    oauth: str = None) -> Credentials:
    oauth = oauth or os.environ.get('APCA_API_OAUTH_TOKEN')

    key_id = key_id or os.environ.get('APCA_API_KEY_ID')
    if key_id is None and oauth is None:
        raise ValueError('Key ID must be given to access Alpaca trade API',
                         ' (env: APCA_API_KEY_ID)')

    secret_key = secret_key or os.environ.get('APCA_API_SECRET_KEY')
    if secret_key is None and oauth is None:
        raise ValueError('Secret key must be given to access Alpaca trade API'
                         ' (env: APCA_API_SECRET_KEY')

    return key_id, secret_key, oauth


def get_polygon_credentials(alpaca_key: str = None) -> str:
    try:
        alpaca_key, _, _ = get_credentials(alpaca_key, 'ignored')
    except ValueError:
        pass
    key_id = os.environ.get('POLYGON_KEY_ID') or alpaca_key
    if key_id is None:
        raise ValueError('Key ID must be given to access Polygon API'
                         ' (env: APCA_API_KEY_ID or POLYGON_KEY_ID)')
    return key_id


def get_alpha_vantage_credentials(alpha_vantage_key: str = None) -> str:
    key_id = alpha_vantage_key or os.environ.get('ALPHAVANTAGE_API_KEY')
    if key_id is None:
        raise ValueError('Key ID must be given to access Alpha Vantage API'
                         ' (env: ALPHAVANTAGE_API_KEY)')
    return key_id


def get_api_version(api_version: str) -> str:
    api_version = api_version or os.environ.get('APCA_API_VERSION')
    if api_version is None:
        api_version = 'v2'

    return api_version
