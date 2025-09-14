"""
app/core/redis.py

Redis helper utilities.

⚠️ NOTE:
- If REDIS_URL is missing or invalid, all functions become no-ops.
- This allows local/dev environments to run without Redis enabled.
"""

import redis.asyncio as redis
from app.core.config import settings

# Safe Redis client init
redis_client = None
if settings.redis_url:
    try:
        redis_client = redis.from_url(
            settings.redis_url,
            decode_responses=True
        )
    except Exception as e:
        # Fallback: run without Redis
        redis_client = None
        print(f"⚠️ Redis init failed: {e}")


async def set_value(key: str, value: str, expire_seconds: int = 300):
    """Set value with expiry (default 5 minutes)."""
    if not redis_client:
        return
    await redis_client.set(key, value, ex=expire_seconds)


async def get_value(key: str):
    """Get value by key."""
    if not redis_client:
        return None
    return await redis_client.get(key)


async def delete_value(key: str):
    """Delete a key."""
    if not redis_client:
        return
    await redis_client.delete(key)
