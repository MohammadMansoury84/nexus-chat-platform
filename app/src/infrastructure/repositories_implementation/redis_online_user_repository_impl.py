from uuid import UUID

import redis.asyncio as aioredis
from src.domain.repositories_Interface.redis_online_user_repository import (
    RedisOnlineUserRepository,
)


class RedisOnlineUserRepositoryImpl(RedisOnlineUserRepository):
    def __init__(self, redis_client: aioredis.Redis):
        self._redis = redis_client
        self._ONLINE_KEY = "online_users"

    async def add_online_user(self, user_id: UUID) -> None:
        await self._redis.sadd(self._ONLINE_KEY, str(user_id))

    async def remove_online_user(self, user_id: UUID) -> None:
        await self._redis.srem(self._ONLINE_KEY, str(user_id))

    async def get_online_user_ids(self) -> set[UUID]:
        members = await self._redis.smembers(self._ONLINE_KEY)
        return {UUID(m) for m in members}

    async def is_user_logged_in(self, user_id: UUID) -> bool:
        return await self._redis.sismember(self._ONLINE_KEY, str(user_id))
