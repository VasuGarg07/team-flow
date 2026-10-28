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

def delete_cache(key: str) -> None:
    try:
        redis_client.delete(key)
    except RedisError:
        pass

def projects_cache_key(workspace_id: int) -> str:
    return f"workspace:{workspace_id}:projects"

def allow_request(key: str, limit: int = 10, window: int = 60) -> bool:
    try:
        count = redis_client.incr(key)
        redis_client.expire(key, window, nx=True)
        return count <= limit
    except RedisError:
        return True

def seconds_until_reset(key: str, window: int) -> int:
    try:
        ttl = redis_client.ttl(key)
    except RedisError:
        return window
    return ttl if ttl > 0 else window