#!/usr/bin/env python

import os
import sys
import pprint
import asyncio
import logging
import argparse

import pandas as pd

from datetime import datetime

from alpaca_trade_api import StreamConn

# For some fun colors...
from colorama import Fore, Style, init as ColoramaInit


ColoramaInit(autoreset=True)

# Make this global
opt = None


def ts():
    return pd.Timestamp.now()


def log(*args, **kwargs):
    print(ts(), " ", *args, **kwargs)


def debug(*args, **kwargs):
    print(ts(), " ", *args, file=sys.stderr, **kwargs)


def ms2date(ms, fmt='%Y-%m-%d'):
    if isinstance(ms, pd.Timestamp):
        return ms.strftime(fmt)
    else:
        return datetime.fromtimestamp(ms/1000).strftime(fmt)


async def on_minute(conn, channel, bar):
    symbol = bar.symbol
    close = bar.close

    try:
        percent = (close - bar.dailyopen)/close  * 100
        up = 1 if bar.open > bar.dailyopen else -1
    except:  # noqa
        percent = 0
        up = 0

    if up > 0:
        bar_color = f'{Style.BRIGHT}{Fore.CYAN}'
    elif up < 0:
        bar_color = f'{Style.BRIGHT}{Fore.RED}'
    else:
        bar_color = f'{Style.BRIGHT}{Fore.WHITE}'

    print(f'{channel:<6s} {ms2date(bar.end)}  {bar.symbol:<10s} '
          f'{percent:>8.2f}% {bar.open:>8.2f} {bar.close:>8.2f} '
          f' {bar.volume:<10d}'
          f'  {(Fore.GREEN+"above VWAP") if close > bar.vwap else (Fore.RED+"below VWAP")}')


async def on_tick(conn, channel, bar):
    try:
        percent = (bar.close - bar.dailyopen)/bar.close * 100
    except:  # noqa
        percent = 0

    print(f'{channel:<6s} {ms2date(bar.end)}  {bar.symbol:<10s} '
          f'{percent:>8.2f}% {bar.open:>8.2f} {bar.close:>8.2f} '
          f' {bar.volume:<10d}')


async def on_data(conn, channel, data):
    if opt.debug or not (channel in ('AM', 'Q', 'A', 'T')):
        debug("debug: ", pprint.pformat(data))


def reloadWatch(prog, cmd):
    async def watch_command():
        startingmodtime = os.path.getmtime(prog)

        while True:
            modtime = os.path.getmtime(prog)
            if modtime != startingmodtime:
                debug(f'Reloading {" ".join(cmd)} ...')

                os.execv(prog, cmd)

            await asyncio.sleep(5)

    return watch_command


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--all", "-a",
        help="Watch the A.* feed as well, which can overwelm and backup during active times",
        action='store_true')

    parser.add_argument(
        "--debug",
        help="Prints debug messages",
        action='store_true')

    opt = parser.parse_args()

    conn = StreamConn()

    # This is another way to setup wrappers for websocket callbacks, handy if conn is not global.
    on_minute = conn.on(r'AM$')(on_minute)
    on_tick = conn.on(r'A$')(on_tick)
    on_data = conn.on(r'.*')(on_data)

    # This is an example of how you can add your own async functions into the loop
    # This one just watches this program for edits and tries to restart it
    asyncio.ensure_future(reloadWatch(__file__, sys.argv)())

    try:
        if opt.all:
            # Note to see all these channels, you'd need to add a handler
            # above or use --debug!
            conn.run(['Q.*', 'T.*', 'AM.*', 'A.*'])
        else:
            conn.run(['AM.*'])
    except Exception as e:
        print(e)
