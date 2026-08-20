from abc import ABC, abstractmethod
from uuid import UUID


class RedisOnlineUserRepository(ABC):
    @abstractmethod
    async def add_online_user(self, user_id: UUID) -> None:
        pass

    @abstractmethod
    async def remove_online_user(self, user_id: UUID) -> None:
        pass

    @abstractmethod
    async def get_online_user_ids(self) -> set[UUID]:
        pass
