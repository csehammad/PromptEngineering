import redis.asyncio as redis
from typing import Optional, Any
from app.core.config import settings
import json
import logging

logger = logging.getLogger(__name__)

# Redis connection pool
redis_client: Optional[redis.Redis] = None


async def get_redis_client() -> redis.Redis:
    """Get Redis client with connection pooling"""
    global redis_client
    if redis_client is None:
        try:
            redis_client = redis.from_url(
                settings.redis_url,
                password=settings.redis_password,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True,
                health_check_interval=30
            )
            # Test connection
            await redis_client.ping()
            logger.info("Redis connection established")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            redis_client = None
            raise
    return redis_client


async def get_cache(key: str) -> Optional[str]:
    """Get value from cache"""
    try:
        client = await get_redis_client()
        value = await client.get(key)
        return value
    except Exception as e:
        logger.warning(f"Cache get error for key {key}: {e}")
        return None


async def set_cache(key: str, value: str, expire: int = 3600) -> bool:
    """Set value in cache with expiration"""
    try:
        client = await get_redis_client()
        await client.setex(key, expire, value)
        return True
    except Exception as e:
        logger.warning(f"Cache set error for key {key}: {e}")
        return False


async def delete_cache(key: str) -> bool:
    """Delete value from cache"""
    try:
        client = await get_redis_client()
        result = await client.delete(key)
        return result > 0
    except Exception as e:
        logger.warning(f"Cache delete error for key {key}: {e}")
        return False


async def increment_rate_limit(key: str, expire: int = 60) -> int:
    """Increment rate limit counter"""
    try:
        client = await get_redis_client()
        pipe = client.pipeline()
        pipe.incr(key)
        pipe.expire(key, expire)
        results = await pipe.execute()
        return results[0]
    except Exception as e:
        logger.warning(f"Rate limit increment error for key {key}: {e}")
        return 0


async def get_rate_limit(key: str) -> int:
    """Get current rate limit count"""
    try:
        client = await get_redis_client()
        value = await client.get(key)
        return int(value) if value else 0
    except Exception as e:
        logger.warning(f"Rate limit get error for key {key}: {e}")
        return 0


async def clear_rate_limit(key: str) -> bool:
    """Clear rate limit counter"""
    return await delete_cache(key)


async def cache_json(key: str, data: Any, expire: int = 3600) -> bool:
    """Cache JSON data"""
    try:
        json_data = json.dumps(data, default=str)
        return await set_cache(key, json_data, expire)
    except Exception as e:
        logger.warning(f"Cache JSON error for key {key}: {e}")
        return False


async def get_cached_json(key: str) -> Optional[Any]:
    """Get cached JSON data"""
    try:
        data = await get_cache(key)
        if data:
            return json.loads(data)
        return None
    except Exception as e:
        logger.warning(f"Get cached JSON error for key {key}: {e}")
        return None


async def close_redis():
    """Close Redis connection"""
    global redis_client
    if redis_client:
        try:
            await redis_client.close()
            redis_client = None
            logger.info("Redis connection closed")
        except Exception as e:
            logger.error(f"Error closing Redis connection: {e}") 