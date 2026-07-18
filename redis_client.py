import os
from redis.asyncio import Redis

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Global Redis client
redis_client: Redis = None

async def init_redis():
    global redis_client
    redis_client = Redis.from_url(REDIS_URL, decode_responses=True)

async def close_redis():
    global redis_client
    if redis_client:
        await redis_client.close()

async def get_redis():
    return redis_client
