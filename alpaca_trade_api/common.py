import os


def get_base_url():
    return os.environ.get(
        'APCA_API_BASE_URL', 'https://api.alpaca.markets').rstrip('/')


def get_data_url():
    return os.environ.get(
        'APCA_API_DATA_URL', 'https://data.alpaca.markets').rstrip('/')


def get_credentials(key_id=None, secret_key=None, oauth=None):
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


def get_polygon_credentials(alpaca_key=None):
    try:
        alpaca_key, _, _ = get_credentials(alpaca_key, 'ignored')
    except ValueError:
        pass
    key_id = os.environ.get('POLYGON_KEY_ID') or alpaca_key
    if key_id is None:
        raise ValueError('Key ID must be given to access Polygon API'
                         ' (env: APCA_API_KEY_ID or POLYGON_KEY_ID)')
    return key_id


def get_api_version(api_version):
    api_version = api_version or os.environ.get('APCA_API_VERSION')
    if api_version is None:
        api_version = 'v2'

    return api_version
