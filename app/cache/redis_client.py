import redis.asyncio as redis
from app.core.config import get_settings

settings = get_settings()

redis_pool = redis.ConnectionPool.from_url(
    settings.REDIS_URL,
    decode_responses=True,
    max_connections=20,
)

async def get_redis() -> redis.Redis:
    return redis.Redis(connection_pool=redis_pool)
