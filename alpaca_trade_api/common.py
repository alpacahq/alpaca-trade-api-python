import os


def get_base_url():
    return os.environ.get(
        'ALPACA_API_BASE_URL', 'https://api.alpaca.markets')
