import redis.asyncio as redis
from app.core.config import settings

# Redis connection via REDIS_URL in .env
redis_client = redis.from_url(
    settings.redis_url,
    decode_responses=True
)

async def set_value(key: str, value: str, expire_seconds: int = 300):
    """Set value with expiry (default 5 minutes)."""
    await redis_client.set(key, value, ex=expire_seconds)

async def get_value(key: str):
    """Get value by key."""
    return await redis_client.get(key)

async def delete_value(key: str):
    """Delete a key."""
    await redis_client.delete(key)
