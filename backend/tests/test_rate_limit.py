import pytest
from redis import RedisError

from app.cache import allow_request, seconds_until_reset


class FakeRedis:
    def __init__(self) -> None:
        self.counts: dict[str, int] = {}
        self.expiries: dict[str, int] = {}

    def incr(self, key: str) -> int:
        self.counts[key] = self.counts.get(key, 0) + 1
        return self.counts[key]

    def expire(self, key: str, seconds: int, nx: bool = False) -> bool:
        if nx and key in self.expiries:
            return False
        self.expiries[key] = seconds
        return True

    def ttl(self, key: str) -> int:
        return self.expiries.get(key, -2)


class BrokenRedis:
    def incr(self, key: str) -> int:
        raise RedisError("down")

    def expire(self, key: str, seconds: int, nx: bool = False) -> bool:
        raise RedisError("down")

    def ttl(self, key: str) -> int:
        raise RedisError("down")


@pytest.fixture
def fake_redis(monkeypatch: pytest.MonkeyPatch) -> FakeRedis:
    fake = FakeRedis()
    monkeypatch.setattr("app.cache.redis_client", fake)
    return fake


def test_requests_up_to_the_limit_are_allowed(fake_redis: FakeRedis) -> None:
    results = [allow_request("login:1.1.1.1", 5, 60) for _ in range(5)]
    assert results == [True, True, True, True, True]


def test_request_over_the_limit_is_blocked(fake_redis: FakeRedis) -> None:
    for _ in range(5):
        allow_request("login:1.1.1.1", 5, 60)
    assert allow_request("login:1.1.1.1", 5, 60) is False


def test_different_keys_are_counted_separately(fake_redis: FakeRedis) -> None:
    for _ in range(5):
        allow_request("login:1.1.1.1", 5, 60)
    assert allow_request("login:2.2.2.2", 5, 60) is True


def test_the_window_is_set_once_on_the_counter(fake_redis: FakeRedis) -> None:
    allow_request("login:1.1.1.1", 5, 60)
    allow_request("login:1.1.1.1", 5, 30)
    assert fake_redis.expiries == {"login:1.1.1.1": 60}


def test_request_is_allowed_when_redis_is_down(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("app.cache.redis_client", BrokenRedis())
    assert allow_request("login:1.1.1.1", 5, 60) is True


def test_seconds_until_reset_uses_the_remaining_time(fake_redis: FakeRedis) -> None:
    fake_redis.expiries["login:1.1.1.1"] = 42
    assert seconds_until_reset("login:1.1.1.1", 60) == 42


def test_seconds_until_reset_falls_back_to_the_window_when_the_key_is_gone(fake_redis: FakeRedis) -> None:
    assert seconds_until_reset("login:1.1.1.1", 60) == 60


def test_seconds_until_reset_falls_back_to_the_window_when_redis_is_down(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("app.cache.redis_client", BrokenRedis())
    assert seconds_until_reset("login:1.1.1.1", 60) == 60