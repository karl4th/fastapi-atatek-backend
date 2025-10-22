from __future__ import annotations
from typing import Any, Dict, Optional
from redis.asyncio import Redis
from src.app.config import settings




_redis: Optional[Redis] = None

async def get_redis() -> Redis:
    """Return singleton Redis client (lazy)."""
    global _redis
    if _redis is None:
        _redis = Redis(
            host=settings.get_redis_host,
            port=6379,
            db=0,
            decode_responses=True,
            # production-grade tweaks
            socket_keepalive=True,
            socket_keepalive_options={},
            retry_on_timeout=True,
            max_connections=50,
        )
    return _redis
