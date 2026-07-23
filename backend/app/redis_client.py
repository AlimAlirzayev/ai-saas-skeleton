import redis.asyncio as redis
from .config import settings

redis_client = redis.Redis(
    host=settings.redis_host,
    port=settings.redis_port,
    decode_responses=True
)


async def get_cached(key: str) -> str | None:
    return await redis_client.get(key)


async def set_cached(key: str, value: str, ttl: int = 3600):
    await redis_client.setex(key, ttl, value)