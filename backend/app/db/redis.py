"""
Redis cache connection
"""

import redis.asyncio as redis
from redis.exceptions import ConnectionError

from app.core.config import settings
from app.core.logging import logger


class RedisCache:
    """Redis cache manager."""
    
    def __init__(self):
        self.client: redis.Redis = None
    
    async def connect(self):
        """Connect to Redis."""
        try:
            logger.info(f"Connecting to Redis at {settings.REDIS_URL}")
            self.client = await redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True,
                socket_connect_timeout=3,  # 减少等待时间
            )
            
            # Verify connection
            await self.client.ping()
            
            logger.info("Redis connection established successfully")
            
        except Exception as e:
            logger.warning(f"Redis unavailable, running without cache: {e}")
            # Don't raise - app can work without Redis
            self.client = None
    
    async def close(self):
        """Close Redis connection."""
        if self.client:
            await self.client.close()
            logger.info("Redis connection closed")
    
    async def get(self, key: str) -> str:
        """Get value from cache."""
        if not self.client:
            return None
        return await self.client.get(key)
    
    async def set(self, key: str, value: str, expire: int = 3600):
        """Set value in cache."""
        if not self.client:
            return
        await self.client.set(key, value, ex=expire)
    
    async def delete(self, key: str):
        """Delete value from cache."""
        if not self.client:
            return
        await self.client.delete(key)


# Global Redis instance
redis_client = RedisCache()


async def connect_redis():
    """Initialize Redis connection."""
    await redis_client.connect()


async def close_redis():
    """Close Redis connection."""
    await redis_client.close()
