from redis import Redis, RedisError

from .config import app_settings

redis_client = Redis.from_url(
    app_settings.REDIS_URL, 
    decode_responses=True,
    socket_connect_timeout=0.5,
    socket_timeout=0.5,
)

def read_cache(key: str) -> str | None:
    try:
        return redis_client.get(key)
    except RedisError:
        return None

def write_cache(key: str, value: str, ttl_seconds: int = 60) -> None:
    try: 
        redis_client.set(key, value, ex=ttl_seconds)
    except RedisError:
        pass