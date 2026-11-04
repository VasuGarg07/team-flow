class InMemoryRedis:
    def __init__(self) -> None:
        self.values: dict[str, str] = {}
        self.counters: dict[str, int] = {}
        self.expiries: dict[str, int] = {}
        self.published: list[tuple[str, str]] = []

    def get(self, key: str) -> str | None:
        return self.values.get(key)

    def set(self, key: str, value: str, ex: int | None = None) -> bool:
        self.values[key] = value
        if ex is not None:
            self.expiries[key] = ex
        return True

    def delete(self, key: str) -> int:
        existed = key in self.values
        self.values.pop(key, None)
        return int(existed)

    def incr(self, key: str) -> int:
        self.counters[key] = self.counters.get(key, 0) + 1
        return self.counters[key]

    def expire(self, key: str, seconds: int, nx: bool = False) -> bool:
        if nx and key in self.expiries:
            return False
        self.expiries[key] = seconds
        return True

    def ttl(self, key: str) -> int:
        return self.expiries.get(key, -2)

    def publish(self, channel: str, message: str) -> int:
        self.published.append((channel, message))
        return 0

    def events_for(self, channel: str) -> list[str]:
        return [message for published_channel, message in self.published if published_channel == channel]
