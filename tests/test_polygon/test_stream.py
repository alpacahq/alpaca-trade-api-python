from alpaca_trade_api.polygon import stream
import asyncio

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
def NATS():
    with mock.patch('alpaca_trade_api.polygon.stream.NATS') as NATS:
        yield NATS


def _run(coro):
    return asyncio.get_event_loop().run_until_complete(coro)


def test_stream(NATS):
    NATS().connect = AsyncMock()
    s = stream.Stream('api-key')
    _run(s.connect())
    assert NATS().connect.mock.called

    @s.on('subject')
    async def on_subject(stream, subject, data):
        assert data.flag

    msg = mock.Mock(subject='subject', data=b'{"flag": true}')
    _run(s._dispatch(msg))

    s.deregister('subject')

    with pytest.raises(ValueError):
        s.register('illegal', lambda x: x)

    NATS().subscribe = AsyncMock(return_value=1)
    NATS().unsubscribe = AsyncMock()
    _run(s.subscribe(['topics']))
    assert s._ssids[0] == 1
    _run(s.subscribe([]))
    assert len(s._ssids) == 0
