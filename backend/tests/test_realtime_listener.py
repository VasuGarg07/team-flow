import asyncio

import pytest

from app.realtime import listen_for_events


class BrokenRedisClient:
    closed = False

    def pubsub(self) -> None:
        raise ValueError("something unexpected")

    async def aclose(self) -> None:
        BrokenRedisClient.closed = True


class FakeAsyncRedis:
    @staticmethod
    def from_url(url: str, decode_responses: bool) -> BrokenRedisClient:
        return BrokenRedisClient()


def test_listener_logs_unexpected_errors_retries_and_closes_the_client(monkeypatch: pytest.MonkeyPatch) -> None:
    async def stop_instead_of_sleeping(seconds: float) -> None:
        raise asyncio.CancelledError

    monkeypatch.setattr("app.realtime.AsyncRedis", FakeAsyncRedis)
    monkeypatch.setattr("app.realtime.asyncio.sleep", stop_instead_of_sleeping)
    BrokenRedisClient.closed = False

    with pytest.raises(asyncio.CancelledError):
        asyncio.run(listen_for_events())

    assert BrokenRedisClient.closed is True