"""
app/core/rate_limit.py

Rate limiting via Redis.

⚠️ NOTE:
- If REDIS_URL is missing or Redis is unavailable, rate limiting is skipped
  (fail-open) so OTP/auth flows are not blocked.
"""

import redis
from fastapi import HTTPException
from app.core.config import settings
from app.core.logging import logger

# -----------------------------
# Redis Client (safe init)
# -----------------------------
redis_client = None
if settings.redis_url:
    try:
        redis_client = redis.StrictRedis.from_url(
            settings.redis_url,
            decode_responses=True
        )
    except Exception as e:
        redis_client = None
        logger.warning(f"⚠️ Failed to init Redis client for rate limiting: {e}")


# -----------------------------
# Rate limit helper
# -----------------------------
def check_rate_limit(key: str, limit: int = 5, window: int = 60) -> None:
    """
    Rate limit helper.

    - key: unique identifier (e.g., "otp:+919876543210" or "otp-ip:127.0.0.1")
    - limit: max allowed requests
    - window: time window in seconds

    If Redis is unavailable, no rate limiting is enforced (fail-open).
    """
    if not redis_client:
        return  # skip rate limiting if Redis not configured

    try:
        # increment the counter
        current = redis_client.incr(key)
        if current == 1:
            # set expiry only on first request
            redis_client.expire(key, window)

        if current > limit:
            ttl = redis_client.ttl(key)
            raise HTTPException(
                status_code=429,
                detail=f"Rate limit exceeded. Try again in {ttl} seconds.",
            )
    except redis.RedisError as e:
        # If Redis is down, fail OPEN (no blocking auth flow)
        logger.error(f"Redis error in rate limiting: {e}")
        return
