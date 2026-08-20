import redis.asyncio as aioredis

_redis_client = aioredis.from_url(
    "redis://localhost:6379", decode_responses=True, protocol=2
)


async def get_redis():
    return _redis_client
