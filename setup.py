#!/usr/bin/env python

import ast
import re
from setuptools import setup

_version_re = re.compile(r'__version__\s+=\s+(.*)')

with open('alpaca_trade_api/__init__.py', 'rb') as f:
    version = str(ast.literal_eval(_version_re.search(
        f.read().decode('utf-8')).group(1)))

with open('README.md') as readme_file:
    README = readme_file.read()

setup(
    name='alpaca-trade-api',
    version=version,
    description='Alpaca API python client',
    long_description=README,
    long_description_content_type='text/markdown',
    author='Alpaca',
    author_email='oss@alpaca.markets',
    url='https://github.com/alpacahq/alpaca-trade-api-python',
    keywords='financial,timeseries,api,trade',
    packages=['alpaca_trade_api', 'alpaca_trade_api.polygon'],
    install_requires=[
        'asyncio-nats-client',
        'pandas',
        'requests',
        'urllib3<1.25',
        'websocket-client',
        'websockets',
    ],
    tests_require=[
        'pytest',
        'pytest-cov',
        'requests-mock',
        'coverage>=4.4.1',
        'mock>=1.0.1',
        'flake8',
    ],
    setup_requires=['pytest-runner', 'flake8'],
)
