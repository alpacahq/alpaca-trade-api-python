import os


def get_base_url():
    return os.environ.get(
        'APCA_API_BASE_URL', 'https://api.alpaca.markets').rstrip('/')


def get_data_url():
    return os.environ.get(
        'APCA_API_DATA_URL', 'https://data.alpaca.markets').rstrip('/')


def get_credentials(key_id=None, secret_key=None):
    key_id = key_id or os.environ.get('APCA_API_KEY_ID')
    if key_id is None:
        raise ValueError('Key ID must be given to access Alpaca trade API')
    secret_key = secret_key or os.environ.get('APCA_API_SECRET_KEY')
    if secret_key is None:
        raise ValueError('Secret key must be given to access Alpaca trade API')
    return key_id, secret_key
