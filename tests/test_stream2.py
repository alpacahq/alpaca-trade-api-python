from alpaca_trade_api.stream2 import StreamConn
from alpaca_trade_api.entity import Account
import asyncio
import json

import pytest
from unittest import mock


def AsyncMock(*args, **kwargs):
    """Create an async function mock."""
    m = mock.MagicMock(*args, **kwargs)

    async def mock_coro(*args, **kwargs):
        return m(*args, **kwargs)

    mock_coro.mock = m
    return mock_coro


@pytest.fixture
def websockets():
    with mock.patch('alpaca_trade_api.stream2.websockets') as websockets:
        yield websockets


def _run(coro):
    return asyncio.get_event_loop().run_until_complete(coro)


def test_stream(websockets):
    # _connect
    connect = AsyncMock()
    websockets.connect = connect
    ws = connect.mock()
    ws.send = AsyncMock()
    ws.recv = AsyncMock(return_value=json.dumps({
        'stream': 'authentication',
        'data':   {
            'status': 'authorized',
        }
    }).encode())

    conn = StreamConn('key-id', 'secret-key')
    conn = conn.trading_ws
    conn._consume_msg = AsyncMock()

    @conn.on('authorized')
    async def on_auth(conn, stream, msg):
        on_auth.msg = msg

    _run(conn._connect())
    assert on_auth.msg.status == 'authorized'
    assert conn._consume_msg.mock.called

    conn.deregister('authorized')
    assert len(conn._handlers) == 0

    with pytest.raises(ValueError):
        conn.register('nonasync', lambda x: x)

    # _consume_msg
    conn = StreamConn('key-id', 'secret-key')
    ws = mock.Mock()
    conn._ws = ws
    ws.recv = AsyncMock(return_value=json.dumps({
        'stream': 'raise',
        'data':   {
            'key': 'value',
        }
    }))
    ws.close = AsyncMock()

    class TestException(Exception):
        pass

    @conn.on('raise')
    async def on_raise(conn, stream, msg):
        raise TestException()

    # _ensure_ws
    conn = StreamConn('key-id', 'secret-key')
    conn.trading_ws._connect = AsyncMock()
    _run(conn._ensure_ws(conn.trading_ws))
    assert conn.trading_ws._connect.mock.called

    # subscribe
    conn = StreamConn('key-id', 'secret-key').trading_ws
    conn._ensure_ws = AsyncMock()
    conn._ws = mock.Mock()
    conn._ws.send = AsyncMock()
    conn._ensure_nats = AsyncMock()

    _run(conn.subscribe(['Q.*', 'account_updates']))
    assert conn._ws.send.mock.called

    # close
    conn = StreamConn('key-id', 'secret-key').trading_ws
    conn._ws = mock.Mock()
    conn._ws.close = AsyncMock()
    _run(conn.close())
    assert conn._ws is None

    # _cast
    conn = StreamConn('key-id', 'secret-key').trading_ws
    ent = conn._cast('account_updates', {})
    assert isinstance(ent, Account)
    ent = conn._cast('other', {'key': 'value'})
    assert ent.key == 'value'
